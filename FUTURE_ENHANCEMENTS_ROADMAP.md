# 🚀 FUTURE ENHANCEMENTS ROADMAP
## Movistar System - Next-Generation Features

**Current Version**: 2.0 - Production Ready  
**Target Version**: 3.0 - Enterprise Platform  
**Timeline**: 6-12 months

---

## 🎯 VISION

Transform the Movistar sales processing system from a **batch processing tool** into a **comprehensive enterprise data platform** with:

- 🌐 **Web-based UI** for non-technical users
- 🤖 **AI/ML capabilities** for intelligent automation
- 📊 **Real-time analytics** dashboards
- 🔌 **API-first architecture** for integrations
- ☁️ **Cloud-native** deployment
- 🔄 **Real-time processing** capabilities
- 📈 **Predictive insights** and recommendations

---

## 📊 IMPROVEMENT MATRIX

| Area | Current State | Target State | Impact | Effort |
|------|--------------|--------------|--------|--------|
| **User Interface** | CLI only | Web UI + Mobile | 🔥🔥🔥 High | Medium |
| **ML/AI** | Rule-based | ML-powered validation | 🔥🔥🔥 High | High |
| **Processing** | Batch | Real-time + Batch | 🔥🔥 Medium | High |
| **API** | None | REST + GraphQL | 🔥🔥🔥 High | Medium |
| **Database** | File-based | PostgreSQL/MongoDB | 🔥🔥🔥 High | Medium |
| **Monitoring** | Logs | Dashboards + Alerts | 🔥🔥 Medium | Low |
| **Testing** | Basic | 80%+ coverage | 🔥🔥 Medium | Medium |
| **CI/CD** | Manual | Automated | 🔥🔥 Medium | Low |
| **Cloud** | Local | AWS/Azure/GCP | 🔥🔥🔥 High | High |
| **Analytics** | Basic stats | BI Dashboards | 🔥🔥 Medium | Medium |

---

## 🎨 PHASE 1: USER EXPERIENCE (Priority: HIGH)

### 1.1 Web-Based UI (React + FastAPI)

**Goal**: Allow non-technical users to upload files, monitor processing, and download results

**Features**:
```
┌─────────────────────────────────────────────────────────────┐
│                    MOVISTAR DATA PLATFORM                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 Upload Files                                            │
│  ┌──────────────┐ ┌──────────────┐                         │
│  │ Tipificador  │ │   Digital    │                          │
│  │ Drag & Drop  │ │  Drag & Drop │                          │
│  └──────────────┘ └──────────────┘                         │
│                                                              │
│  ⚙️ Processing Options                                      │
│  ☑ Validate phone numbers                                   │
│  ☑ Generate novedades file                                  │
│  ☑ Run quality checks                                       │
│  ☑ Email results when complete                              │
│                                                              │
│  📊 Real-time Progress                                      │
│  ████████████████░░░░ 80% - Validating records...          │
│                                                              │
│  ✅ Valid: 950 | ❌ Invalid: 50 | ⏱️ ETA: 2 min             │
│                                                              │
│  📥 Download Results                                        │
│  [Contact Log] [FORMATO MOVISTAR] [SVAS] [Novedades]       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Technology Stack**:
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python)
- **State Management**: Redux or Zustand
- **File Upload**: Chunked uploads with progress
- **Real-time Updates**: WebSockets

**Implementation**:
```python
# backend/api/main.py
from fastapi import FastAPI, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Movistar Data Platform")

@app.post("/api/v1/upload/tipificador")
async def upload_tipificador(file: UploadFile):
    """Upload and validate tipificador file."""
    # Save file
    # Trigger async processing
    # Return job ID
    pass

@app.websocket("/ws/job/{job_id}")
async def job_progress(websocket: WebSocket, job_id: str):
    """Stream job progress to client."""
    # Send real-time updates
    pass

@app.get("/api/v1/jobs/{job_id}/results")
async def get_results(job_id: str):
    """Download processed results."""
    pass
```

**Frontend Example**:
```typescript
// frontend/src/components/FileUpload.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export const FileUpload = () => {
  const onDrop = useCallback(async (files: File[]) => {
    const formData = new FormData();
    formData.append('file', files[0]);
    
    const response = await fetch('/api/v1/upload/tipificador', {
      method: 'POST',
      body: formData,
    });
    
    const { job_id } = await response.json();
    
    // Connect to WebSocket for progress
    const ws = new WebSocket(`ws://localhost:8000/ws/job/${job_id}`);
    ws.onmessage = (event) => {
      const progress = JSON.parse(event.data);
      console.log(`Progress: ${progress.percentage}%`);
    };
  }, []);
  
  const { getRootProps, getInputProps } = useDropzone({ onDrop });
  
  return (
    <div {...getRootProps()} className="border-2 border-dashed p-8">
      <input {...getInputProps()} />
      <p>Drag & drop Tipificador file here</p>
    </div>
  );
};
```

**Benefits**:
- ✅ No technical knowledge required
- ✅ Real-time feedback
- ✅ Self-service for operations team
- ✅ Reduced support requests

---

### 1.2 Interactive Dashboards (Plotly Dash or Streamlit)

**Goal**: Real-time visibility into data quality, processing metrics, and trends

**Dashboard Views**:

1. **Executive Dashboard**
   - Total sales processed
   - Quality score trends
   - Rejection rate over time
   - Top rejection reasons

2. **Operations Dashboard**
   - Current processing jobs
   - Records by status (valid/invalid)
   - Validation error breakdown
   - Novedades trends

3. **Quality Dashboard**
   - Data quality metrics
   - Null rate trends
   - Duplicate detection
   - Outlier analysis

4. **Business Intelligence**
   - Sales by product (TU MASCOTA, TU HOGAR, etc.)
   - Sales by line type (MOVIL/FIJA/DIGITAL)
   - Regional analysis
   - Asesor performance

**Implementation**:
```python
# dashboards/quality_dashboard.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Movistar Quality Dashboard", layout="wide")

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Quality Score", "87.5%", "+2.3%")
with col2:
    st.metric("Valid Records", "950", "+50")
with col3:
    st.metric("Rejection Rate", "5.0%", "-1.2%")
with col4:
    st.metric("Processing Time", "2.3 min", "-0.5 min")

# Quality trend chart
fig = px.line(
    quality_history,
    x='date',
    y='quality_score',
    title='Quality Score Trend (Last 30 Days)'
)
st.plotly_chart(fig, use_container_width=True)

# Rejection reasons breakdown
fig = px.bar(
    rejection_stats,
    x='reason',
    y='count',
    title='Top Rejection Reasons'
)
st.plotly_chart(fig, use_container_width=True)
```

**Benefits**:
- ✅ Real-time visibility
- ✅ Data-driven decisions
- ✅ Proactive issue detection
- ✅ Executive reporting

---

## 🤖 PHASE 2: AI/ML CAPABILITIES (Priority: HIGH)

### 2.1 Machine Learning-Powered Validation

**Goal**: Use ML to improve validation accuracy and detect complex patterns

**ML Models**:

1. **Phone Number Classifier**
   ```python
   # ml/models/phone_classifier.py
   from sklearn.ensemble import RandomForestClassifier
   import joblib
   
   class PhoneNumberClassifier:
       """
       ML model to classify phone numbers as MOVIL/FIJA/INVALID.
       
       Features:
       - First digit
       - Prefix (first 3 digits)
       - Length
       - Has 957 prefix
       - Numeric patterns
       """
       
       def __init__(self):
           self.model = RandomForestClassifier(n_estimators=100)
       
       def train(self, X_train, y_train):
           """Train on historical data."""
           self.model.fit(X_train, y_train)
       
       def predict(self, phone_number: str) -> dict:
           """Predict phone type with confidence."""
           features = self.extract_features(phone_number)
           prediction = self.model.predict([features])[0]
           confidence = self.model.predict_proba([features]).max()
           
           return {
               'tipo_linea': prediction,
               'confidence': confidence,
               'needs_manual_review': confidence < 0.8
           }
   ```

2. **Anomaly Detection**
   ```python
   # ml/models/anomaly_detector.py
   from sklearn.ensemble import IsolationForest
   
   class AnomalyDetector:
       """
       Detect anomalous records that may have data quality issues.
       
       Detects:
       - Unusual service code assignments
       - Suspicious asesor names
       - Outlier sale amounts
       - Temporal anomalies
       """
       
       def detect_anomalies(self, df: pd.DataFrame) -> pd.Series:
           """Return boolean series of anomalous records."""
           features = self.extract_features(df)
           predictions = self.model.predict(features)
           return predictions == -1  # -1 indicates anomaly
   ```

3. **Name/Login Validator (NLP)**
   ```python
   # ml/models/name_validator.py
   from transformers import pipeline
   
   class NLPNameValidator:
       """
       Use NLP to validate names are real human names.
       
       Detects:
       - Fake names
       - Gibberish
       - Test data
       """
       
       def __init__(self):
           self.classifier = pipeline("text-classification", model="name-classifier")
       
       def is_valid_name(self, name: str) -> tuple[bool, float]:
           """Check if name is valid with confidence score."""
           result = self.classifier(name)[0]
           is_valid = result['label'] == 'REAL_NAME'
           confidence = result['score']
           return is_valid, confidence
   ```

4. **Service Code Recommender**
   ```python
   # ml/models/code_recommender.py
   class ServiceCodeRecommender:
       """
       Recommend correct service code based on historical patterns.
       
       Learns from:
       - Historical code assignments
       - Product descriptions
       - Customer segments
       - Sales patterns
       """
       
       def recommend_code(
           self,
           tipo_venta: str,
           tipo_linea: str,
           context: dict
       ) -> dict:
           """Recommend code with confidence and explanation."""
           # ML-based recommendation
           features = self.extract_features(tipo_venta, tipo_linea, context)
           prediction = self.model.predict([features])[0]
           confidence = self.model.predict_proba([features]).max()
           
           # Get rule-based code
           rule_based_code = self.service_mapper.get_code(tipo_venta, tipo_linea)
           
           # Compare
           if prediction != rule_based_code[0]:
               return {
                   'recommended_code': prediction,
                   'rule_based_code': rule_based_code[0],
                   'confidence': confidence,
                   'needs_review': True,
                   'reason': 'ML model disagrees with rules'
               }
           
           return {
               'recommended_code': prediction,
               'confidence': confidence,
               'needs_review': False
           }
   ```

5. **Duplicate Detection (Advanced)**
   ```python
   # ml/models/fuzzy_duplicate_detector.py
   from fuzzywuzzy import fuzz
   
   class FuzzyDuplicateDetector:
       """
       Detect duplicates using fuzzy matching.
       
       Detects:
       - Near-duplicate phone numbers (typos)
       - Similar customer names
       - Temporal duplicates (same customer, different times)
       """
       
       def find_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
           """Find potential duplicates with similarity scores."""
           duplicates = []
           
           for idx, row in df.iterrows():
               for idx2, row2 in df.iloc[idx+1:].iterrows():
                   # Check multiple fields
                   phone_similarity = fuzz.ratio(str(row['telefono']), str(row2['telefono']))
                   name_similarity = fuzz.ratio(row['nombre_cliente'], row2['nombre_cliente'])
                   
                   if phone_similarity > 80 or name_similarity > 85:
                       duplicates.append({
                           'record_1': idx,
                           'record_2': idx2,
                           'phone_similarity': phone_similarity,
                           'name_similarity': name_similarity,
                           'confidence': (phone_similarity + name_similarity) / 2
                       })
           
           return pd.DataFrame(duplicates)
   ```

**Benefits**:
- ✅ Higher accuracy than rule-based
- ✅ Learns from patterns
- ✅ Detects complex anomalies
- ✅ Reduces manual review

---

### 2.2 Predictive Analytics

**Goal**: Predict trends and provide insights

**Capabilities**:

1. **Sales Forecasting**
   ```python
   # ml/analytics/forecaster.py
   from prophet import Prophet
   
   class SalesForecaster:
       """Forecast sales volume for next month."""
       
       def forecast(self, historical_data: pd.DataFrame) -> pd.DataFrame:
           """Forecast next 30 days."""
           model = Prophet()
           model.fit(historical_data[['ds', 'y']])
           
           future = model.make_future_dataframe(periods=30)
           forecast = model.predict(future)
           
           return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
   ```

2. **Quality Degradation Prediction**
   ```python
   # ml/analytics/quality_predictor.py
   class QualityPredictor:
       """Predict if data quality will degrade."""
       
       def predict_quality_issues(self, recent_metrics: pd.DataFrame) -> dict:
           """Predict quality issues in next batch."""
           # Time series analysis
           features = self.extract_features(recent_metrics)
           risk_score = self.model.predict_proba([features])[0][1]
           
           return {
               'risk_level': 'HIGH' if risk_score > 0.7 else 'MEDIUM' if risk_score > 0.4 else 'LOW',
               'risk_score': risk_score,
               'predicted_rejection_rate': self.predict_rejection_rate(features),
               'recommendations': self.get_recommendations(risk_score)
           }
   ```

3. **Churn Detection**
   ```python
   # ml/analytics/churn_detector.py
   class ChurnDetector:
       """Detect asesores with unusual patterns (potential churn)."""
       
       def detect_at_risk_asesores(self, sales_history: pd.DataFrame) -> pd.DataFrame:
           """Identify asesores with declining performance."""
           # Analyze trends per asesor
           # Detect drop in volume
           # Detect increase in error rate
           pass
   ```

**Benefits**:
- ✅ Proactive planning
- ✅ Early warning system
- ✅ Resource optimization
- ✅ Strategic insights

---

## 🔌 PHASE 3: API & INTEGRATION (Priority: HIGH)

### 3.1 REST API (FastAPI)

**Goal**: Enable programmatic access and integrations

**Endpoints**:

```python
# api/v1/endpoints.py
from fastapi import FastAPI, UploadFile, BackgroundTasks
from typing import List

app = FastAPI(title="Movistar Data Platform API", version="3.0")

# Data Upload
@app.post("/api/v1/data/upload", response_model=JobResponse)
async def upload_data(
    file: UploadFile,
    file_type: str,  # tipificador, digital
    background_tasks: BackgroundTasks
):
    """
    Upload data file for processing.
    
    Returns job ID for tracking progress.
    """
    job_id = await create_job(file, file_type)
    background_tasks.add_task(process_file, job_id)
    return {"job_id": job_id, "status": "queued"}

# Validation
@app.post("/api/v1/validate/phone", response_model=PhoneValidationResponse)
async def validate_phone(phone: str):
    """Validate single phone number."""
    validator = EnhancedPhoneValidator()
    result = validator.validate(phone)
    return result

@app.post("/api/v1/validate/batch", response_model=BatchValidationResponse)
async def validate_batch(phones: List[str]):
    """Validate batch of phone numbers."""
    validator = EnhancedPhoneValidator()
    results = [validator.validate(p) for p in phones]
    return {"results": results}

# Service Codes
@app.get("/api/v1/codes/get", response_model=ServiceCodeResponse)
async def get_service_code(tipo_venta: str, tipo_linea: str):
    """Get correct service code."""
    mapper = ServiceCodeMapper()
    code, program = mapper.get_code(tipo_venta, tipo_linea)
    return {"code": code, "program": program}

# Jobs
@app.get("/api/v1/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job processing status."""
    status = await get_status(job_id)
    return status

@app.get("/api/v1/jobs/{job_id}/download/{file_type}")
async def download_result(job_id: str, file_type: str):
    """Download processed file."""
    return FileResponse(f"output/{job_id}/{file_type}.xlsx")

# Analytics
@app.get("/api/v1/analytics/quality", response_model=QualityMetrics)
async def get_quality_metrics(start_date: str, end_date: str):
    """Get quality metrics for date range."""
    metrics = await calculate_quality_metrics(start_date, end_date)
    return metrics

@app.get("/api/v1/analytics/sales", response_model=SalesMetrics)
async def get_sales_metrics(start_date: str, end_date: str):
    """Get sales metrics."""
    metrics = await calculate_sales_metrics(start_date, end_date)
    return metrics

# Lineage
@app.get("/api/v1/lineage/{dataset_id}", response_model=LineageGraph)
async def get_lineage(dataset_id: str):
    """Get data lineage for dataset."""
    tracker = LineageTracker()
    lineage = tracker.get_lineage_for(dataset_id)
    return lineage

# Audit
@app.get("/api/v1/audit/events", response_model=List[AuditEvent])
async def get_audit_events(
    start_date: str,
    end_date: str,
    category: str = None
):
    """Get audit events."""
    logger = AuditLogger()
    events = logger.get_events(start_date, end_date, category)
    return events
```

**Authentication & Authorization**:
```python
# api/auth.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
):
    """Verify JWT token and check permissions."""
    # Verify token
    # Check scopes
    # Return user
    pass

@app.post("/api/v1/data/upload")
async def upload_data(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    """Upload requires authentication."""
    pass
```

**Benefits**:
- ✅ Programmatic access
- ✅ Third-party integrations
- ✅ Automation possibilities
- ✅ Mobile app support

---

### 3.2 GraphQL API

**Goal**: Flexible querying for complex data needs

```python
# api/graphql/schema.py
import strawberry
from typing import List

@strawberry.type
class SaleRecord:
    id: str
    tipo_venta: str
    tipo_linea: str
    codigo_servicio: str
    telefono: str
    nombre_cliente: str
    nombre_asesor: str
    fecha_venta: str
    es_valido: bool

@strawberry.type
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

@strawberry.type
class Query:
    @strawberry.field
    def sales(
        self,
        tipo_linea: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> List[SaleRecord]:
        """Query sales with filters."""
        # Query logic
        pass
    
    @strawberry.field
    def quality_metrics(self, date_range: str) -> QualityMetrics:
        """Get quality metrics."""
        pass

@strawberry.type
class Mutation:
    @strawberry.mutation
    def validate_record(self, record: SaleRecordInput) -> ValidationResult:
        """Validate a sales record."""
        pass
    
    @strawberry.mutation
    def process_file(self, file_id: str) -> JobResponse:
        """Trigger file processing."""
        pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

**Benefits**:
- ✅ Flexible queries
- ✅ Reduced over-fetching
- ✅ Strong typing
- ✅ Introspection

---

## 💾 PHASE 4: DATABASE INTEGRATION (Priority: HIGH)

### 4.1 PostgreSQL for Transactional Data

**Goal**: Replace file-based storage with robust database

**Schema Design**:

```sql
-- Database schema
CREATE DATABASE movistar_platform;

-- Sales records
CREATE TABLE sales_records (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    tipo_venta VARCHAR(50) NOT NULL,
    tipo_linea VARCHAR(20) NOT NULL CHECK (tipo_linea IN ('MOVIL', 'FIJA', 'DIGITAL')),
    codigo_servicio VARCHAR(10) NOT NULL,
    programa VARCHAR(100),
    telefono VARCHAR(15) NOT NULL,
    nombre_cliente VARCHAR(255) NOT NULL,
    nombre_asesor VARCHAR(255) NOT NULL,
    login_asesor VARCHAR(50),
    fecha_venta TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Validation
    es_valido BOOLEAN DEFAULT TRUE,
    validacion_telefono BOOLEAN DEFAULT TRUE,
    validacion_asesor BOOLEAN DEFAULT TRUE,
    validacion_login BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    source_file VARCHAR(255),
    processed_by VARCHAR(100),
    
    CONSTRAINT fk_job FOREIGN KEY (job_id) REFERENCES processing_jobs(job_id)
);

-- Indexes for performance
CREATE INDEX idx_sales_tipo_linea ON sales_records(tipo_linea);
CREATE INDEX idx_sales_fecha_venta ON sales_records(fecha_venta);
CREATE INDEX idx_sales_es_valido ON sales_records(es_valido);
CREATE INDEX idx_sales_job_id ON sales_records(job_id);

-- Novedades (rejected records)
CREATE TABLE novedades (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    record_data JSONB NOT NULL,  -- Original record
    motivo_rechazo TEXT NOT NULL,
    validacion_flags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    
    CONSTRAINT fk_job FOREIGN KEY (job_id) REFERENCES processing_jobs(job_id)
);

-- Processing jobs
CREATE TABLE processing_jobs (
    job_id VARCHAR(100) PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    total_records INTEGER,
    valid_records INTEGER,
    invalid_records INTEGER,
    processing_time_seconds NUMERIC,
    error_message TEXT,
    completed_at TIMESTAMP
);

-- Quality metrics (time series)
CREATE TABLE quality_metrics (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100),
    metric_date DATE NOT NULL,
    quality_score NUMERIC(5,2),
    null_rate NUMERIC(5,4),
    duplicate_rate NUMERIC(5,4),
    rejection_rate NUMERIC(5,4),
    avg_processing_time NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_job FOREIGN KEY (job_id) REFERENCES processing_jobs(job_id)
);

-- Audit log
CREATE TABLE audit_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    category VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    description TEXT,
    metadata JSONB,
    severity VARCHAR(20)
);

-- Service code mapping (versioned)
CREATE TABLE service_codes (
    id SERIAL PRIMARY KEY,
    tipo_linea VARCHAR(20) NOT NULL,
    tipo_venta VARCHAR(100) NOT NULL,
    codigo VARCHAR(10) NOT NULL,
    programa VARCHAR(100) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(tipo_linea, tipo_venta, valid_from)
);
```

**Implementation**:

```python
# database/models.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Numeric, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SaleRecord(Base):
    __tablename__ = 'sales_records'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(100), nullable=False)
    tipo_venta = Column(String(50), nullable=False)
    tipo_linea = Column(String(20), nullable=False)
    codigo_servicio = Column(String(10), nullable=False)
    telefono = Column(String(15), nullable=False)
    nombre_cliente = Column(String(255), nullable=False)
    nombre_asesor = Column(String(255), nullable=False)
    fecha_venta = Column(DateTime, nullable=False)
    es_valido = Column(Boolean, default=True)
    created_at = Column(DateTime)

# database/repository.py
class SalesRepository:
    """Repository for sales records."""
    
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_sales_batch(self, records: List[dict]) -> int:
        """Save batch of sales records."""
        session = self.Session()
        try:
            sale_records = [SaleRecord(**record) for record in records]
            session.bulk_save_objects(sale_records)
            session.commit()
            return len(records)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_sales_by_job(self, job_id: str) -> List[SaleRecord]:
        """Get all sales for a job."""
        session = self.Session()
        try:
            return session.query(SaleRecord).filter_by(job_id=job_id).all()
        finally:
            session.close()
    
    def get_quality_trends(self, days: int = 30) -> pd.DataFrame:
        """Get quality metrics trend."""
        query = """
        SELECT 
            DATE(created_at) as date,
            AVG(CASE WHEN es_valido THEN 100 ELSE 0 END) as valid_percentage,
            COUNT(*) as total_records
        FROM sales_records
        WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
        GROUP BY DATE(created_at)
        ORDER BY date
        """
        return pd.read_sql(query, self.engine, params=(days,))
```

**Benefits**:
- ✅ ACID compliance
- ✅ Complex queries
- ✅ Historical analysis
- ✅ Data integrity

---

### 4.2 MongoDB for Unstructured Data

**Goal**: Store logs, lineage, and flexible schemas

```python
# database/mongo_client.py
from pymongo import MongoClient

class MongoRepository:
    """Repository for MongoDB operations."""
    
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client['movistar_platform']
    
    def save_lineage(self, lineage_entry: dict):
        """Save lineage entry."""
        self.db.lineage.insert_one(lineage_entry)
    
    def save_audit_event(self, event: dict):
        """Save audit event."""
        self.db.audit_events.insert_one(event)
    
    def get_lineage_graph(self, dataset_id: str) -> dict:
        """Get complete lineage graph."""
        pipeline = [
            {"$match": {"target": dataset_id}},
            {
                "$graphLookup": {
                    "from": "lineage",
                    "startWith": "$source",
                    "connectFromField": "source",
                    "connectToField": "target",
                    "as": "upstream"
                }
            }
        ]
        return list(self.db.lineage.aggregate(pipeline))
```

**Benefits**:
- ✅ Flexible schema
- ✅ Graph queries (lineage)
- ✅ Time-series data
- ✅ Scalable

---

## ☁️ PHASE 5: CLOUD DEPLOYMENT (Priority: MEDIUM)

### 5.1 AWS Architecture

**Goal**: Cloud-native, scalable deployment

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────┘

Internet
    │
    ▼
┌─────────────┐
│ CloudFront  │ → CDN for frontend
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     ALB     │ → Load Balancer
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐ ┌──────┐
│ ECS  │ │ ECS  │ → Containerized API (FastAPI)
│Task 1│ │Task 2│
└───┬──┘ └───┬──┘
    │        │
    └────┬───┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌──────────┐
│   RDS   │         │   S3     │ → File storage
│PostgreSQL         └──────────┘
└─────────┘
    │
    ▼
┌─────────────┐
│  Lambda     │ → Serverless processing
│  Functions  │
└─────────────┘
    │
    ▼
┌─────────────┐
│    SQS      │ → Job queue
└─────────────┘
    │
    ▼
┌─────────────┐
│  Step       │ → Workflow orchestration
│  Functions  │
└─────────────┘
```

**Infrastructure as Code (Terraform)**:

```hcl
# infrastructure/main.tf

# VPC
resource "aws_vpc" "movistar_vpc" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "movistar-platform-vpc"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "movistar_db" {
  identifier        = "movistar-db"
  engine            = "postgres"
  engine_version    = "14"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  
  db_name  = "movistar_platform"
  username = var.db_username
  password = var.db_password
  
  multi_az               = true
  backup_retention_period = 7
  
  tags = {
    Environment = "production"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "movistar_cluster" {
  name = "movistar-platform-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "api" {
  family                   = "movistar-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  
  container_definitions = jsonencode([
    {
      name  = "api"
      image = "movistar-platform-api:latest"
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = aws_db_instance.movistar_db.endpoint
        }
      ]
    }
  ])
}

# S3 Bucket for files
resource "aws_s3_bucket" "movistar_files" {
  bucket = "movistar-platform-files"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    enabled = true
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# Lambda for async processing
resource "aws_lambda_function" "process_file" {
  function_name = "movistar-process-file"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.handler"
  runtime       = "python3.11"
  timeout       = 900  # 15 minutes
  memory_size   = 3008
  
  environment {
    variables = {
      DATABASE_URL = aws_db_instance.movistar_db.endpoint
      S3_BUCKET    = aws_s3_bucket.movistar_files.id
    }
  }
}
```

**Benefits**:
- ✅ Auto-scaling
- ✅ High availability
- ✅ Disaster recovery
- ✅ Global reach

---

## 🔄 PHASE 6: REAL-TIME PROCESSING (Priority: MEDIUM)

### 6.1 Event-Driven Architecture

**Goal**: Process records in real-time as they arrive

**Architecture**:

```
Sales Data Sources
    │
    ├─── Tipificador Upload
    ├─── Digital Sales API
    ├─── Google Sheets Integration
    │
    ▼
┌─────────────┐
│   Kafka     │ → Message broker
│   Topics    │
└──────┬──────┘
       │
   ┌───┴────────────┐
   │                │
   ▼                ▼
┌──────────┐  ┌──────────┐
│ Validation│  │Processing│ → Consumer groups
│ Service   │  │ Service  │
└─────┬────┘  └─────┬────┘
      │             │
      └──────┬──────┘
             │
             ▼
     ┌──────────────┐
     │   Database   │
     │   + Cache    │
     └──────────────┘
```

**Implementation**:

```python
# streaming/kafka_producer.py
from kafka import KafkaProducer
import json

class SalesStreamProducer:
    """Stream sales records to Kafka."""
    
    def __init__(self, bootstrap_servers: list):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def send_record(self, record: dict):
        """Send single record to stream."""
        self.producer.send('sales-records', value=record)
    
    def send_batch(self, records: List[dict]):
        """Send batch of records."""
        for record in records:
            self.send_record(record)
        self.producer.flush()

# streaming/kafka_consumer.py
from kafka import KafkaConsumer

class ValidationConsumer:
    """Consume and validate records in real-time."""
    
    def __init__(self, bootstrap_servers: list):
        self.consumer = KafkaConsumer(
            'sales-records',
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.validator = EnhancedPhoneValidator()
        self.field_validator = FieldValidators()
    
    def start(self):
        """Start consuming and validating."""
        for message in self.consumer:
            record = message.value
            
            # Validate
            phone_result = self.validator.validate(record['telefono'])
            asesor_valid, _ = self.field_validator.validate_asesor_name(record['nombre_asesor'])
            
            # Route to appropriate topic
            if phone_result.is_valid and asesor_valid:
                self.send_to_valid_topic(record)
            else:
                self.send_to_invalid_topic(record, phone_result, asesor_valid)
```

**Benefits**:
- ✅ Real-time validation
- ✅ Immediate feedback
- ✅ Scalable throughput
- ✅ Event sourcing

---

## 📊 PHASE 7: ADVANCED ANALYTICS & BI (Priority: MEDIUM)

### 7.1 Data Warehouse (Snowflake/BigQuery)

**Goal**: Long-term analytics and BI

**Star Schema**:

```sql
-- Fact table
CREATE TABLE fact_sales (
    sale_id BIGINT PRIMARY KEY,
    date_key INT REFERENCES dim_date(date_key),
    product_key INT REFERENCES dim_product(product_key),
    line_type_key INT REFERENCES dim_line_type(line_type_key),
    asesor_key INT REFERENCES dim_asesor(asesor_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    
    -- Measures
    sale_amount DECIMAL(10,2),
    commission DECIMAL(10,2),
    is_valid BOOLEAN,
    processing_time_ms INT
);

-- Dimension tables
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    date DATE,
    year INT,
    quarter INT,
    month INT,
    week INT,
    day_of_week INT,
    is_weekend BOOLEAN
);

CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    tipo_venta VARCHAR(100),
    codigo_servicio VARCHAR(10),
    programa VARCHAR(100),
    category VARCHAR(50)
);

CREATE TABLE dim_line_type (
    line_type_key INT PRIMARY KEY,
    tipo_linea VARCHAR(20),
    description VARCHAR(255)
);

CREATE TABLE dim_asesor (
    asesor_key INT PRIMARY KEY,
    nombre_asesor VARCHAR(255),
    login_asesor VARCHAR(50),
    team VARCHAR(100),
    region VARCHAR(100)
);
```

**BI Views**:

```sql
-- Sales performance view
CREATE VIEW vw_sales_performance AS
SELECT 
    d.year,
    d.month,
    p.tipo_venta,
    lt.tipo_linea,
    COUNT(*) as total_sales,
    SUM(CASE WHEN f.is_valid THEN 1 ELSE 0 END) as valid_sales,
    AVG(f.sale_amount) as avg_sale_amount,
    SUM(f.commission) as total_commission
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_line_type lt ON f.line_type_key = lt.line_type_key
GROUP BY d.year, d.month, p.tipo_venta, lt.tipo_linea;

-- Asesor performance view
CREATE VIEW vw_asesor_performance AS
SELECT 
    a.nombre_asesor,
    a.team,
    d.month,
    COUNT(*) as total_sales,
    AVG(CASE WHEN f.is_valid THEN 100.0 ELSE 0 END) as quality_percentage,
    SUM(f.sale_amount) as total_revenue
FROM fact_sales f
JOIN dim_asesor a ON f.asesor_key = a.asesor_key
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY a.nombre_asesor, a.team, d.month;
```

**Benefits**:
- ✅ Historical analysis
- ✅ Complex aggregations
- ✅ BI tool integration
- ✅ Data lake integration

---

### 7.2 Power BI / Tableau Integration

**Goal**: Executive dashboards

**Dashboards**:

1. **Executive Dashboard**
   - Total sales trend
   - Quality score trend
   - Top products
   - Regional breakdown

2. **Operations Dashboard**
   - Processing jobs status
   - Error rates
   - Throughput metrics
   - Resource utilization

3. **Quality Dashboard**
   - Validation pass rate
   - Top rejection reasons
   - Data quality trends
   - Anomaly alerts

**Implementation**:
```python
# analytics/powerbi_connector.py
class PowerBIConnector:
    """Push data to Power BI datasets."""
    
    def __init__(self, workspace_id: str, dataset_id: str):
        self.workspace_id = workspace_id
        self.dataset_id = dataset_id
    
    def push_sales_data(self, df: pd.DataFrame):
        """Push sales data to Power BI."""
        # Transform to Power BI schema
        # Push via REST API
        pass
```

**Benefits**:
- ✅ Executive visibility
- ✅ Interactive exploration
- ✅ Mobile access
- ✅ Automated reports

---

## 🧪 PHASE 8: COMPREHENSIVE TESTING (Priority: MEDIUM)

### 8.1 Unit Tests (80%+ Coverage)

**Goal**: Test all components

```python
# tests/test_phone_validator.py
import pytest
from src.services import EnhancedPhoneValidator

class TestPhoneValidator:
    def setup_method(self):
        self.validator = EnhancedPhoneValidator()
    
    def test_valid_movil(self):
        """Test valid mobile number."""
        result = self.validator.validate('3001234567')
        assert result.is_valid
        assert result.tipo_linea == 'MOVIL'
        assert result.cleaned_phone == '3001234567'
    
    def test_957_prefix_handling(self):
        """Test 957 prefix is removed correctly."""
        result = self.validator.validate('9573001234567')
        assert result.is_valid
        assert result.cleaned_phone == '3001234567'
    
    def test_invalid_prefix(self):
        """Test invalid mobile prefix."""
        result = self.validator.validate('3991234567')
        assert not result.is_valid
        assert 'Prefijo móvil no válido' in result.reason
    
    @pytest.mark.parametrize("phone,expected_type", [
        ('3001234567', 'MOVIL'),
        ('6012345678', 'FIJA'),
        ('5551234567', 'INVALIDO'),
    ])
    def test_classification(self, phone, expected_type):
        """Test phone classification."""
        result = self.validator.validate(phone)
        assert result.tipo_linea == expected_type

# tests/test_service_code_mapper.py
class TestServiceCodeMapper:
    def setup_method(self):
        self.mapper = ServiceCodeMapper()
    
    def test_movil_codes(self):
        """Test MOVIL service codes."""
        tests = [
            ('TU MASCOTA', 'MOVIL', '3823'),
            ('TU HOGAR', 'MOVIL', '5000'),
            ('TU VEHICULO', 'MOVIL', '5002'),
        ]
        for tipo_venta, tipo_linea, expected_code in tests:
            code, _ = self.mapper.get_code(tipo_venta, tipo_linea)
            assert code == expected_code
    
    def test_fija_codes(self):
        """Test FIJA service codes."""
        code, _ = self.mapper.get_code('TU MASCOTA', 'FIJA')
        assert code == '15639'
```

**Run tests**:
```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Output:
# tests/test_phone_validator.py ✓✓✓✓✓✓✓✓
# tests/test_service_code_mapper.py ✓✓✓✓
# tests/test_field_validators.py ✓✓✓✓✓
# 
# Coverage: 87%
```

---

### 8.2 Integration Tests

```python
# tests/integration/test_pipeline.py
class TestValidationPipeline:
    def test_end_to_end_validation(self):
        """Test complete validation pipeline."""
        # Create test data
        df_test = pd.DataFrame([
            {'telefono': '3001234567', 'nombre_asesor': 'Juan Pérez', 'login_asesor': '12345'},
            {'telefono': '5551234567', 'nombre_asesor': 'Maria Garcia', 'login_asesor': '67890'},
            {'telefono': '9573001234567', 'nombre_asesor': '#N/A', 'login_asesor': 'ABC'},
        ])
        
        # Run validation
        stage = ValidationStage()
        context = PipelineContext()
        context.add_dataframe('tipificador_raw', df_test)
        
        result_context = stage.execute(context)
        
        # Assert
        df_valid = result_context.get_dataframe('tipificador_valid')
        df_invalid = result_context.get_dataframe('tipificador_novedades')
        
        assert len(df_valid) == 1  # Only first record valid
        assert len(df_invalid) == 2  # Two invalid
```

---

## 🔐 PHASE 9: SECURITY & COMPLIANCE (Priority: HIGH)

### 9.1 Security Features

**Capabilities**:

1. **Authentication & Authorization**
   ```python
   # auth/jwt_handler.py
   from jose import jwt
   from passlib.context import CryptContext
   
   class AuthHandler:
       """Handle JWT authentication."""
       
       def create_access_token(self, user_id: str, scopes: list) -> str:
           """Create JWT token."""
           payload = {
               'sub': user_id,
               'scopes': scopes,
               'exp': datetime.utcnow() + timedelta(hours=24)
           }
           return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
       
       def verify_token(self, token: str) -> dict:
           """Verify and decode token."""
           return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
   ```

2. **Data Encryption**
   ```python
   # security/encryption.py
   from cryptography.fernet import Fernet
   
   class DataEncryption:
       """Encrypt sensitive data."""
       
       def encrypt_pii(self, data: str) -> str:
           """Encrypt PII (phone numbers, names)."""
           f = Fernet(ENCRYPTION_KEY)
           return f.encrypt(data.encode()).decode()
       
       def decrypt_pii(self, encrypted_data: str) -> str:
           """Decrypt PII."""
           f = Fernet(ENCRYPTION_KEY)
           return f.decrypt(encrypted_data.encode()).decode()
   ```

3. **Audit Logging**
   - Already implemented ✅
   - Enhanced with security events

4. **Data Masking**
   ```python
   # security/masking.py
   def mask_phone(phone: str) -> str:
       """Mask phone number for display."""
       return f"{phone[:3]}****{phone[-2:]}"
   
   def mask_name(name: str) -> str:
       """Mask customer name."""
       parts = name.split()
       return f"{parts[0]} {'*' * len(parts[-1])}"
   ```

**Benefits**:
- ✅ GDPR compliance
- ✅ Data protection
- ✅ Access control
- ✅ Audit trail

---

## 🎯 IMPLEMENTATION PRIORITIES

### High Priority (3-6 months)
1. ✅ Web UI (React + FastAPI)
2. ✅ REST API
3. ✅ Database Integration (PostgreSQL)
4. ✅ Basic ML (Phone classifier)
5. ✅ Dashboards (Streamlit)

### Medium Priority (6-9 months)
6. ✅ Real-time Processing (Kafka)
7. ✅ Advanced ML (Anomaly detection)
8. ✅ Cloud Deployment (AWS)
9. ✅ GraphQL API
10. ✅ Comprehensive Testing

### Low Priority (9-12 months)
11. ✅ Data Warehouse
12. ✅ Power BI Integration
13. ✅ Mobile App
14. ✅ Advanced Security
15. ✅ Multi-tenant

---

## 💰 ESTIMATED COSTS (Monthly)

### Cloud Infrastructure (AWS)
- **RDS PostgreSQL** (db.t3.medium): $70
- **ECS Fargate** (2 tasks): $60
- **S3 Storage** (500GB): $12
- **CloudFront CDN**: $20
- **Lambda** (1M invocations): $2
- **Total**: ~$160/month

### SaaS Tools
- **Monitoring** (DataDog): $15/host
- **Error Tracking** (Sentry): $26/month
- **CI/CD** (GitHub Actions): Free
- **Total**: ~$40/month

### **Grand Total**: ~$200/month for production deployment

---

## 📊 SUCCESS METRICS

### Technical Metrics
- **Processing Speed**: <5 min for 10k records
- **API Response Time**: <200ms (p95)
- **Uptime**: 99.9%
- **Test Coverage**: >80%
- **Code Quality**: A rating (SonarQube)

### Business Metrics
- **Data Quality Score**: >90%
- **User Adoption**: 50+ active users
- **Error Rate**: <2%
- **Time Saved**: 10+ hours/week
- **ROI**: 5x within 12 months

---

## 🚀 QUICK WINS (Implement First)

1. **Streamlit Dashboard** (1 week)
   - Immediate visibility
   - Low effort, high impact
   
2. **FastAPI REST API** (2 weeks)
   - Enable integrations
   - Foundation for web UI
   
3. **PostgreSQL Migration** (2 weeks)
   - Better data management
   - Enable analytics
   
4. **Automated Tests** (1 week)
   - Prevent regressions
   - Confidence in changes
   
5. **Docker + CI/CD** (1 week)
   - Consistent deployments
   - Faster iterations

---

**Total Enhancement Scope**: 15+ major features  
**Estimated Timeline**: 6-12 months  
**Team Size**: 2-3 developers  
**Investment**: $200/month + development time  

**Next Steps**: Review priorities and select Phase 1 features to implement.
