
### **Proposed Architecture**

```
[IoT Devices] → [Kafka Streams] → [ClickHouse] → [Redis Cache] → [Analytics Service]
                                    ↓
                              [PostgreSQL] (for metadata)
```

### **Key Components**

#### **1. Data Ingestion Layer**
```python
# Kafka Producer for telemetry streaming
class TelemetryProducer:
    def ingest_telemetry(self, device_id, energy_watts, timestamp):
        message = {
            "device_id": device_id,
            "energy_watts": energy_watts,
            "timestamp": timestamp,
            "partition_key": device_id  # For ordered processing
        }
        kafka_producer.send("telemetry_stream", message)
```

#### **2. ClickHouse for Time-Series Analytics**
```sql
-- ClickHouse table optimized for time-series queries
CREATE TABLE telemetry_data (
    device_id String,
    energy_watts Float64,
    timestamp DateTime,
    date Date MATERIALIZED toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY date
ORDER BY (device_id, timestamp)
TTL date + INTERVAL 30 DAY;  -- Auto-cleanup
```

#### **3. Redis Caching Layer**
```python
class AnalyticsCache:
    def get_energy_summary(self, user_id, time_range):
        cache_key = f"energy_summary:{user_id}:{time_range}"
        
        # Check cache first
        cached_result = redis.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Query ClickHouse for real-time data
        result = clickhouse.query("""
            SELECT avg(energy_watts), max(energy_watts), count(*)
            FROM telemetry_data 
            WHERE user_id = %s AND timestamp >= %s
        """, [user_id, time_range])
        
        # Cache for 5 minutes
        redis.setex(cache_key, 300, json.dumps(result))
        return result
```

#### **4. Optimized Analytics Service**
```python
class AnalyticsService:
    def get_real_time_aggregations(self, user_id):
        # 1. Check Redis cache first (fastest)
        cached = self.cache.get_energy_summary(user_id, "last_hour")
        if cached:
            return cached
        
        # 2. Query ClickHouse for real-time data
        return self.clickhouse_client.get_aggregations(user_id)
    
    def generate_alerts(self, device_id):
        # Use ClickHouse for fast time-window queries
        recent_data = self.clickhouse_client.query("""
            SELECT energy_watts 
            FROM telemetry_data 
            WHERE device_id = %s 
            AND timestamp >= now() - INTERVAL 5 MINUTE
        """, [device_id])
        
        if self.detect_anomaly(recent_data):
            self.alert_service.send_alert(device_id)
```


### **Migration Strategy**
1. **Phase 1**: Add Redis caching layer (immediate 5x improvement)
2. **Phase 2**: Migrate to ClickHouse for time-series data
3. **Phase 3**: Implement Kafka streaming pipeline
4. **Phase 4**: Add pre-aggregation jobs
