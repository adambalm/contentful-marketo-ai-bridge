# ActivationLog Audit Trail Technical Specification

This is the technical specification for the comprehensive audit logging system enabling enterprise governance, compliance tracking, and machine learning training data in the AI Content Activation Engine.

> Created: 2025-09-06
> Version: 1.0.0
> Status: Implemented ✅
> Reference: @.agent-os/product/decisions.md ADR-002

## Technical Requirements

### Core Functionality
- **Comprehensive Audit Logging**: Record every content activation with complete decision trail
- **Dual-Use Architecture**: Structured data suitable for both audit compliance and ML training
- **Real-Time Logging**: Immediate capture of activation results and processing metadata
- **Queryable History**: Searchable and analyzable historical activation data

### Data Capture Requirements
- **Complete Workflow Tracking**: Every step of content activation pipeline logged
- **AI Processing Metadata**: Provider selection, model usage, processing times, costs
- **Brand Voice Analysis**: Detailed brand voice scoring and recommendations
- **Platform Publishing**: Marketing platform responses, campaign IDs, success/failure details
- **Error Documentation**: Comprehensive error logging with resolution tracking

### Storage & Format Requirements
- **JSONL Format**: Line-delimited JSON for efficient processing and ML pipeline compatibility
- **Structured Schema**: Consistent data structure enabling reliable analysis and training
- **Temporal Integrity**: Accurate timestamps and processing duration tracking
- **Data Integrity**: Validation and consistency checking for audit reliability

### Performance Requirements
- **Low Latency Logging**: <50ms overhead for audit logging during activation
- **High Throughput**: Support 1000+ activations per hour without performance impact
- **Efficient Storage**: Optimized data structure minimizing storage overhead
- **Fast Retrieval**: Rapid querying for audit reviews and compliance reporting

## Approach

### Architecture Pattern
```python
# ActivationLog data model
class ActivationLog(BaseModel):
    activation_id: str = Field(..., description="Unique identifier for this activation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Input data
    content_input: Dict[str, Any]
    content_source: str = Field(..., description="contentful|manual|api")
    
    # Processing pipeline results
    validation_results: ValidationResult
    ai_enrichment: AIEnrichmentResult
    brand_voice_analysis: BrandVoiceResult
    vision_processing: Optional[VisionProcessingResult] = None
    
    # Output and publishing
    platform_publishing: PlatformPublishingResult
    activation_result: ActivationResult
    
    # Metadata and performance
    processing_metadata: ProcessingMetadata
    performance_metrics: PerformanceMetrics
    
    # ML training preparation
    training_features: Optional[Dict[str, Any]] = None
    quality_scores: Dict[str, float] = {}

class ProcessingMetadata(BaseModel):
    ai_provider: str
    ai_model: str
    marketing_platform: str
    content_type: str
    campaign_tags: List[str]
    processing_duration_ms: int
    error_count: int = 0
    retry_count: int = 0
```

### Implementation Strategy
1. **Structured Logging System**: Implement comprehensive JSONL-based audit logging
2. **Pipeline Integration**: Capture data at every stage of content activation pipeline
3. **ML Training Preparation**: Structure data for future supervised fine-tuning workflows
4. **Query Interface**: Provide efficient querying and analysis capabilities
5. **Compliance Support**: Ensure audit trail meets enterprise governance requirements

### Integration Points
- **Content Activation Pipeline**: Log every activation attempt and result
- **AI Service Integration**: Capture AI provider metadata, costs, and performance
- **Brand Voice Analysis**: Record detailed brand voice analysis and recommendations
- **Marketing Platform**: Log platform publishing results and campaign metadata

## Data Schema Design

### Core ActivationLog Schema
```python
class ActivationLog(BaseModel):
    # Identification and timing
    activation_id: str = Field(..., regex="^act_[0-9a-f]{32}$")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Content source and input
    content_input: ContentInput
    content_source: ContentSource
    content_hash: str = Field(..., description="SHA-256 hash of input content")
    
    # Processing results
    validation_results: ValidationResult
    ai_enrichment: AIEnrichmentResult
    brand_voice_analysis: BrandVoiceResult
    vision_processing: Optional[VisionProcessingResult]
    
    # Publishing and output
    platform_publishing: PlatformPublishingResult
    activation_result: ActivationResult
    
    # System metadata
    processing_metadata: ProcessingMetadata
    performance_metrics: PerformanceMetrics
    error_log: List[ErrorEntry] = []
    
    # ML training support
    training_labels: Optional[Dict[str, Any]] = None
    quality_assessment: QualityAssessment = Field(default_factory=QualityAssessment)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
```

### AI Enrichment Tracking
```python
class AIEnrichmentResult(BaseModel):
    provider: str
    model: str
    processing_time_ms: int
    token_usage: TokenUsage
    cost_estimate: float
    
    # Generated content
    meta_description: Optional[str]
    social_media_posts: List[str] = []
    blog_summary: Optional[str]
    
    # Quality metrics
    generation_confidence: float = Field(ge=0.0, le=1.0)
    content_quality_score: float = Field(ge=0.0, le=1.0)
    
    # Error tracking
    errors: List[str] = []
    retry_count: int = 0

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
class VisionProcessingResult(BaseModel):
    provider: str
    model: str
    processing_time_ms: int
    images_processed: int
    
    # Generated alt text
    alt_text_generated: Dict[str, str]  # image_url -> alt_text
    
    # Quality metrics
    alt_text_quality_scores: Dict[str, float]
    accessibility_compliance: bool
```

### Platform Publishing Tracking
```python
class PlatformPublishingResult(BaseModel):
    platform: str
    publishing_time_ms: int
    
    # Campaign results
    campaign_created: bool
    campaign_id: Optional[str]
    campaign_url: Optional[str]
    
    # Content publishing
    content_published: bool
    content_id: Optional[str]
    content_url: Optional[str]
    
    # Asset management
    assets_uploaded: int
    asset_urls: List[str] = []
    
    # Platform response
    platform_response: Dict[str, Any]
    platform_metadata: Dict[str, Any] = {}
    
    # Success metrics
    estimated_reach: Optional[int]
    performance_predictions: Dict[str, float] = {}
```

### Performance and Quality Metrics
```python
class PerformanceMetrics(BaseModel):
    total_processing_time_ms: int
    validation_time_ms: int
    ai_processing_time_ms: int
    brand_voice_time_ms: int
    platform_publishing_time_ms: int
    
    # Resource usage
    memory_usage_mb: float
    cpu_usage_percent: float
    
    # Quality metrics
    overall_success_rate: float
    error_rate: float
    retry_rate: float

class QualityAssessment(BaseModel):
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    content_quality_factors: Dict[str, float] = {}
    
    # Success indicators
    validation_passed: bool = True
    brand_voice_passed: bool = True
    platform_published: bool = True
    
    # ML training indicators
    suitable_for_training: bool = True
    training_quality_score: float = Field(ge=0.0, le=1.0, default=0.0)
```

## JSONL Storage Implementation

### File Organization
```python
class ActivationLogStorage:
    def __init__(self, base_path: str = "logs/activations"):
        self.base_path = Path(base_path)
        self.current_file = self._get_current_log_file()
    
    def _get_current_log_file(self) -> Path:
        """Get current log file based on date rotation"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.base_path / f"activations-{today}.jsonl"
    
    def log_activation(self, activation_log: ActivationLog) -> None:
        """Write activation log entry to JSONL file"""
        with open(self.current_file, 'a', encoding='utf-8') as f:
            f.write(activation_log.json() + '\n')
    
    def query_activations(
        self, 
        start_date: datetime,
        end_date: datetime,
        filters: Dict[str, Any] = None
    ) -> List[ActivationLog]:
        """Query activation logs with date range and filters"""
        results = []
        
        for log_file in self._get_log_files_in_range(start_date, end_date):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = ActivationLog.parse_raw(line.strip())
                    if self._matches_filters(log_entry, filters):
                        results.append(log_entry)
        
        return results
```

### ML Training Data Preparation
```python
class MLTrainingDataGenerator:
    """Convert ActivationLog entries to ML training datasets"""
    
    def generate_content_quality_dataset(
        self, 
        activation_logs: List[ActivationLog]
    ) -> Dict[str, List]:
        """Generate dataset for content quality prediction"""
        dataset = {
            'features': [],
            'labels': [],
            'metadata': []
        }
        
        for log in activation_logs:
            if log.quality_assessment.suitable_for_training:
                features = self._extract_content_features(log)
                label = log.quality_assessment.overall_quality_score
                metadata = {
                    'activation_id': log.activation_id,
                    'timestamp': log.timestamp,
                    'content_type': log.processing_metadata.content_type
                }
                
                dataset['features'].append(features)
                dataset['labels'].append(label)
                dataset['metadata'].append(metadata)
        
        return dataset
    
    def generate_brand_voice_dataset(
        self, 
        activation_logs: List[ActivationLog]
    ) -> Dict[str, List]:
        """Generate dataset for brand voice analysis improvement"""
        dataset = {
            'content': [],
            'brand_voice_scores': [],
            'recommendations': []
        }
        
        for log in activation_logs:
            if log.brand_voice_analysis and log.brand_voice_analysis.overall_status in ['pass', 'advisory']:
                dataset['content'].append(log.content_input)
                dataset['brand_voice_scores'].append({
                    'professionalism': log.brand_voice_analysis.professionalism.score,
                    'accessibility': log.brand_voice_analysis.accessibility.score,
                    'action_oriented': log.brand_voice_analysis.action_oriented.score,
                    'consistency': log.brand_voice_analysis.consistency.score
                })
                dataset['recommendations'].append(log.brand_voice_analysis.recommendations)
        
        return dataset
```

## Query and Analytics Interface

### Audit Query API
```python
class ActivationLogQuery:
    """Query interface for activation audit logs"""
    
    def __init__(self, storage: ActivationLogStorage):
        self.storage = storage
    
    def get_activation_by_id(self, activation_id: str) -> Optional[ActivationLog]:
        """Retrieve specific activation by ID"""
        # Implementation for ID-based lookup
        pass
    
    def get_activations_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[ActivationLog]:
        """Retrieve activations within date range"""
        return self.storage.query_activations(start_date, end_date)
    
    def get_failed_activations(
        self, 
        start_date: datetime,
        end_date: datetime
    ) -> List[ActivationLog]:
        """Retrieve failed activations for analysis"""
        return self.storage.query_activations(
            start_date, 
            end_date, 
            filters={'activation_result.success': False}
        )
    
    def get_performance_metrics(
        self, 
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate performance analytics from logs"""
        logs = self.get_activations_by_date_range(start_date, end_date)
        
        return {
            'total_activations': len(logs),
            'success_rate': self._calculate_success_rate(logs),
            'avg_processing_time': self._calculate_avg_processing_time(logs),
            'platform_distribution': self._calculate_platform_distribution(logs),
            'ai_provider_usage': self._calculate_ai_provider_usage(logs),
            'brand_voice_compliance': self._calculate_brand_voice_metrics(logs)
        }
```

## Compliance and Governance Integration

### Audit Trail Requirements
```python
class ComplianceAuditTrail:
    """Compliance-focused audit trail functionality"""
    
    def generate_audit_report(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> AuditReport:
        """Generate comprehensive audit report"""
        activations = self.query.get_activations_by_date_range(start_date, end_date)
        
        return AuditReport(
            report_period=DateRange(start_date, end_date),
            total_activations=len(activations),
            successful_activations=len([a for a in activations if a.activation_result.success]),
            failed_activations=len([a for a in activations if not a.activation_result.success]),
            
            # Compliance metrics
            brand_voice_compliance_rate=self._calculate_compliance_rate(activations, 'brand_voice'),
            data_processing_compliance=self._validate_data_processing_compliance(activations),
            error_resolution_rate=self._calculate_error_resolution_rate(activations),
            
            # Quality metrics
            content_quality_metrics=self._calculate_quality_metrics(activations),
            performance_metrics=self._calculate_performance_metrics(activations),
            
            # Detailed logs
            detailed_logs=activations if len(activations) <= 1000 else None,
            summary_statistics=self._calculate_summary_statistics(activations)
        )
    
    def validate_data_integrity(self, activation_logs: List[ActivationLog]) -> ValidationReport:
        """Validate audit log data integrity"""
        integrity_issues = []
        
        for log in activation_logs:
            # Validate required fields
            if not log.activation_id or not log.timestamp:
                integrity_issues.append(f"Missing required fields in {log.activation_id}")
            
            # Validate data consistency
            if log.processing_metadata.processing_duration_ms < 0:
                integrity_issues.append(f"Invalid processing time in {log.activation_id}")
            
            # Validate business logic consistency
            if log.activation_result.success and log.error_log:
                integrity_issues.append(f"Inconsistent success/error state in {log.activation_id}")
        
        return ValidationReport(
            total_logs_validated=len(activation_logs),
            integrity_issues=integrity_issues,
            data_quality_score=1.0 - (len(integrity_issues) / len(activation_logs))
        )
```

## Security and Privacy Considerations

### Data Privacy
```python
class PrivacyProtection:
    """Privacy protection for audit logs"""
    
    def anonymize_activation_log(self, log: ActivationLog) -> ActivationLog:
        """Remove personally identifiable information"""
        anonymized_log = log.copy(deep=True)
        
        # Remove user identification
        anonymized_log.user_id = None
        anonymized_log.session_id = None
        
        # Sanitize content while preserving structure
        anonymized_log.content_input = self._sanitize_content(log.content_input)
        
        # Preserve analytics value while protecting privacy
        return anonymized_log
    
    def _sanitize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize content while preserving analytical value"""
        sanitized = content.copy()
        
        # Replace actual content with content type and length information
        if 'title' in sanitized:
            sanitized['title'] = f"<TITLE:{len(sanitized['title'])} chars>"
        if 'body' in sanitized:
            sanitized['body'] = f"<BODY:{len(sanitized['body'])} chars>"
        
        # Preserve campaign tags and metadata for analysis
        return sanitized
```

## Acceptance Criteria

### Functional Acceptance
- [ ] Complete audit trail captured for every content activation attempt
- [ ] JSONL format enables efficient querying and ML pipeline integration
- [ ] All AI processing metadata captured including provider, model, costs, performance
- [ ] Brand voice analysis results fully preserved with recommendations
- [ ] Marketing platform publishing results and campaign metadata logged

### Performance Acceptance
- [ ] Audit logging adds <50ms overhead to content activation process
- [ ] System supports 1000+ activations per hour without performance degradation
- [ ] Log querying returns results within 2 seconds for typical date ranges
- [ ] Storage optimization keeps log file sizes manageable (<100MB per day)
- [ ] Memory usage remains constant regardless of activation volume

### Compliance Acceptance
- [ ] Audit trail meets enterprise governance requirements for content publishing
- [ ] Data integrity validation ensures reliable audit information
- [ ] Privacy protection mechanisms preserve user confidentiality
- [ ] Historical data retention supports compliance and legal requirements
- [ ] Query interface provides comprehensive audit reporting capabilities

### ML Training Acceptance
- [ ] Log structure supports supervised fine-tuning dataset generation
- [ ] Quality assessment enables training data filtering and selection
- [ ] Feature extraction provides relevant inputs for model training
- [ ] Data format compatibility with common ML training frameworks
- [ ] Training dataset generation scales to thousands of examples

## Future Enhancement Framework

### Advanced Analytics
```python
# Framework for advanced audit log analytics
class ActivationAnalytics:
    def performance_trend_analysis(self, days: int = 30) -> TrendAnalysis:
        """Analyze performance trends over time"""
        pass
    
    def content_quality_correlation(self) -> CorrelationAnalysis:
        """Analyze correlation between input quality and output success"""
        pass
    
    def ai_provider_effectiveness(self) -> ProviderAnalysis:
        """Compare AI provider performance and cost effectiveness"""
        pass
    
    def predictive_quality_modeling(self) -> QualityPredictionModel:
        """Build model to predict content activation success"""
        pass
```

### Integration Extensions
```python
# Framework for extended integrations
class AuditLogIntegrations:
    def export_to_data_warehouse(self, warehouse_config: Dict):
        """Export audit logs to enterprise data warehouse"""
        pass
    
    def integrate_with_bi_tools(self, bi_config: Dict):
        """Integration with business intelligence platforms"""
        pass
    
    def compliance_monitoring_alerts(self, alert_config: Dict):
        """Real-time compliance monitoring and alerting"""
        pass
```