# =========================================================
# Telco Churn Prediction App - Streamlit UI
# Uses Gold Layer features directly for reliable predictions
# =========================================================

import streamlit as st
import os
from pyspark.sql import SparkSession
from pyspark.ml.classification import GBTClassificationModel
from pyspark.sql.functions import col, when, abs as spark_abs

# Page configuration
st.set_page_config(
    page_title="Telco Churn Predictor",
    page_icon="📊",
    layout="wide"
)

# MinIO Configuration
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio1:9000")
MODEL_PATH = os.getenv("MODEL_PATH", "s3a://telco-churn/models/gbt_churn_resource_friendly")
GOLD_PATH = "s3a://telco-churn/gold/telco_churn"

# Cache Spark session and model
@st.cache_resource
def get_spark_session():
    """Initialize Spark session with MinIO configuration."""
    jars = [
        "/opt/spark/jars/hadoop-aws-3.3.4.jar",
        "/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar",
        "/opt/spark/jars/delta-spark_2.12-3.0.0.jar",
        "/opt/spark/jars/delta-storage-3.0.0.jar"
    ]
    jars_str = ",".join(jars)
    
    spark = (
        SparkSession.builder
        .appName("TelcoChurn_Streamlit")
        .master("local[*]")
        .config("spark.jars", jars_str)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.endpoint", f"http://{MINIO_ENDPOINT}")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.driver.memory", "1g")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark

@st.cache_resource
def load_model(_spark):
    """Load the trained GBT model from MinIO."""
    try:
        model = GBTClassificationModel.load(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

@st.cache_resource
def load_gold_data(_spark):
    """Load Gold Layer data."""
    try:
        df = _spark.read.format("delta").load(GOLD_PATH)
        return df
    except Exception as e:
        st.error(f"Error loading Gold Layer: {e}")
        return None

# =========================================================
# UI Components
# =========================================================

st.title("🔮 Telco Customer Churn Predictor")
st.markdown("### Predict whether a customer is likely to churn")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## About")
    st.markdown("""
    This app uses a **Gradient Boosted Trees** model trained on historical customer data.
    
    **Model Performance:**
    - AUC-ROC: 87.88%
    - Accuracy: 80.59%
    - F1-Score: 80.49%
    """)
    st.markdown("---")
    st.markdown("**Data Source:** MinIO/Delta Lake")

# Main form
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👤 Customer Profile")
    senior_citizen = st.selectbox("Senior Citizen", ["No", "Yes"])
    partner = st.selectbox("Partner", ["No", "Yes"])
    dependents = st.selectbox("Dependents", ["No", "Yes"])
    tenure = st.slider("Tenure (months)", 0, 72, 12)

with col2:
    st.subheader("📱 Services")
    phone_service = st.selectbox("Phone Service", ["Yes", "No"])
    multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    online_security = st.selectbox("Online Security", ["No", "Yes"])
    online_backup = st.selectbox("Online Backup", ["No", "Yes"])

with col3:
    st.subheader("💳 Billing")
    contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
    paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
    payment_method = st.selectbox("Payment Method", [
        "Electronic check", 
        "Mailed check", 
        "Bank transfer (automatic)", 
        "Credit card (automatic)"
    ])
    monthly_charges = st.number_input("Monthly Charges ($)", 0.0, 200.0, 70.0, step=5.0)
    total_charges = st.number_input("Total Charges ($)", 0.0, 10000.0, monthly_charges * tenure, step=50.0)

st.markdown("---")

# Prediction button
if st.button("🔮 Predict Churn", type="primary", use_container_width=True):
    with st.spinner("Loading model and making prediction..."):
        try:
            spark = get_spark_session()
            model = load_model(spark)
            gold_df = load_gold_data(spark)
            
            if model is None or gold_df is None:
                st.error("Failed to load model or data.")
            else:
                # Find the closest matching customer profile from Gold Layer
                # This ensures we use properly encoded features
                
                # Calculate target values
                target_tenure = float(tenure)
                target_monthly = float(monthly_charges)
                target_senior = 1 if senior_citizen == "Yes" else 0
                target_partner = 1 if partner == "Yes" else 0
                target_dependents = 1 if dependents == "Yes" else 0
                target_contract = contract
                target_payment = payment_method
                target_internet = internet_service
                target_paperless = 1 if paperless_billing == "Yes" else 0
                
                # Filter Gold Layer to find similar profiles
                # Start with exact matches on key categorical features
                filtered_df = gold_df.filter(
                    (col("Contract") == target_contract) &
                    (col("InternetService") == target_internet) &
                    (col("PaymentMethod") == target_payment)
                )
                
                # If no exact matches, use the full dataset
                if filtered_df.count() == 0:
                    filtered_df = gold_df
                
                # Find the closest match by tenure and monthly charges
                closest_match = (
                    filtered_df
                    .withColumn("tenure_diff", spark_abs(col("tenure") - target_tenure))
                    .withColumn("charge_diff", spark_abs(col("MonthlyCharges") - target_monthly))
                    .withColumn("score", col("tenure_diff") + col("charge_diff") / 10)
                    .orderBy("score")
                    .limit(1)
                )
                
                # Make prediction using the matched row's features
                predictions = model.transform(closest_match)
                result = predictions.select(
                    "prediction", "probability", 
                    "Contract", "tenure", "MonthlyCharges"
                ).collect()[0]
                
                prediction = int(result["prediction"])
                probability = result["probability"][1]
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Prediction Results")
                
                result_col1, result_col2 = st.columns(2)
                
                with result_col1:
                    if prediction == 1:
                        st.error("## ⚠️ HIGH CHURN RISK")
                        st.markdown(f"### Churn Probability: **{probability*100:.1f}%**")
                    else:
                        st.success("## ✅ LOW CHURN RISK")
                        st.markdown(f"### Retention Probability: **{(1-probability)*100:.1f}%**")
                
                with result_col2:
                    st.metric("Churn Probability", f"{probability*100:.1f}%", 
                              delta=f"{'High Risk' if probability > 0.5 else 'Low Risk'}")
                    st.progress(probability)
                
                # Show matched profile info
                st.markdown("---")
                st.subheader("📋 Analysis Based On")
                st.info(f"""
                **Similar Customer Profile:**
                - Contract: {result["Contract"]}
                - Tenure: {int(result["tenure"])} months
                - Monthly Charges: ${result["MonthlyCharges"]:.2f}
                """)
                
                # Recommendations
                st.subheader("💡 Recommended Actions")
                
                if prediction == 1:
                    if contract == "Month-to-month":
                        st.warning("🎯 Offer contract upgrade discount (1-2 year)")
                    if payment_method == "Electronic check":
                        st.warning("🎯 Suggest automatic payment methods")
                    if tenure <= 12:
                        st.warning("🎯 New customer - offer loyalty program")
                    if monthly_charges > 80:
                        st.warning("🎯 Review package - consider bundle discounts")
                else:
                    st.info("✅ Customer is stable. Continue regular engagement.")
                    
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Built with Streamlit | Model: Spark ML GBT | Data: Delta Lake on MinIO"
    "</div>", 
    unsafe_allow_html=True
)
