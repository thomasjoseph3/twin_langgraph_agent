# Test Questions for Digital Twin AI Agent

## About This File
Copy and paste these questions into your terminal or API calls to test the agent's capabilities.
All questions assume you're viewing **Heat Exchanger HX00-A3 (entity_id: 40976504)**.

---

## 📊 Category 1: Current State Queries

### Basic Current State
1. **What is the current temperature?**
   - Tests: Entity context, reading telemetry data

2. **What is the current state of this heat exchanger?**
   - Tests: Full entity overview, formatting

3. **Is this equipment healthy?**
   - Tests: Health score interpretation, derived metrics

4. **What's the current efficiency?**
   - Tests: KPI reading, understanding efficiency metrics

5. **Show me all current temperatures**
   - Tests: Multiple telemetry fields extraction

### Alerts & Issues
6. **Are there any active alerts?**
   - Tests: Alert detection and severity understanding

7. **What maintenance is needed?**
   - Tests: Prescription reading, maintenance recommendations

8. **What's causing the performance deterioration?**
   - Tests: Alert analysis, diagnostic reasoning

### Specific Metrics
9. **What's the noise level right now?**
   - Tests: Specific telemetry reading

10. **What's the fan power consumption?**
    - Tests: Telemetry field identification

11. **What's the approach temperature?**
    - Tests: KPI reading

12. **How much remaining useful life does it have?**
    - Tests: Derived metric (RUL) reading

---

## 📈 Category 2: Historical Data Queries

### Simple Historical
13. **Show me the noise compliance for the last week**
    - Tests: ISO 8601 duration (P7D), KPI historical query, date calculation

14. **What was the average temperature yesterday?**
    - Tests: Natural language date parsing, telemetry historical query

15. **Get the efficiency trend for the past month**
    - Tests: KPI history, P1M duration, trend analysis

16. **Show me the health score history for the last 7 days**
    - Tests: Derived metric history, P1D buckets

### Advanced Historical
17. **What was the maximum noise level last week?**
    - Tests: "max" aggregation, ISO duration

18. **Show me the minimum efficiency in the past 3 days**
    - Tests: "min" aggregation, date calculation

19. **What's the average fan power over the last 2 weeks?**
    - Tests: Telemetry history, P14D duration

20. **Has the vibration increased over time?**
    - Tests: Trend detection, multiple telemetry fields

---

## 🔍 Category 3: Analytical & Comparison Queries

### Analysis
21. **Analyze the performance over the last month**
    - Tests: Multi-metric analysis, insights generation

22. **What trends do you see in the data?**
    - Tests: Pattern recognition, proactive metric selection

23. **Is the equipment degrading?**
    - Tests: Trend analysis, health score + RUL interpretation

24. **What's the relationship between temperature and efficiency?**
    - Tests: Multi-metric correlation

### Comparisons
25. **Compare current efficiency with last week's average**
    - Tests: Current vs historical comparison, calculation

26. **How does today's performance compare to yesterday?**
    - Tests: Day-to-day comparison, multiple metrics

27. **Compare the health score now vs last month**
    - Tests: Derived metric comparison across time

---

## 🎯 Category 4: Complex Multi-Step Queries

28. **Show me the current KPIs and how they've changed over the past week**
    - Tests: Current state + historical + comparison

29. **What are the top 3 concerning metrics based on current state and trends?**
    - Tests: Priority assessment, multi-metric analysis

30. **Explain why the health score is low**
    - Tests: Diagnostic reasoning, multiple data point correlation

31. **What happened last week that caused the alert?**
    - Tests: Historical investigation, alert correlation

32. **Show me all critical metrics and their 7-day trends**
    - Tests: Multiple metrics, historical analysis, formatting

---

## 🧪 Category 5: Edge Cases & Natural Language

### Natural Language Variations
33. **How's it doing?**
    - Tests: Vague query handling, proactive metric selection

34. **Give me a health check**
    - Tests: Understanding intent, comprehensive assessment

35. **What's wrong with it?**
    - Tests: Problem identification from alerts + metrics

36. **Is everything normal?**
    - Tests: Anomaly detection, threshold understanding

### Field Name Variations
37. **What's the inlet temperature?**
    - Tests: Fuzzy field matching (coilBundle.fluidInletTempC)

38. **How fast are the fans running?**
    - Tests: Understanding "fan speed" → fans.fanSpeedPercent

39. **What's the noise?**
    - Tests: Understanding "noise" → casing.noiseLevelDB or noiseCompliance

40. **Is it using too much power?**
    - Tests: Understanding "power" → fans.fanPowerKW

---

## 🚀 How to Test

### Using curl:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current temperature?",
    "entity_context": {
      "entity_id": 40976504,
      "entity_name": "Heat Exchanger HX00-A3",
      "entity_type": "HeatExchanger"
    }
  }'
```

### Using Python:
```python
import requests

def ask(question):
    response = requests.post('http://localhost:8000/query', json={
        "query": question,
        "entity_context": {
            "entity_id": 40976504,
            "entity_name": "Heat Exchanger HX00-A3"
        }
    })
    return response.json()['response']

# Test
print(ask("What is the current temperature?"))
```

### Interactive Testing:
Open `http://localhost:8000/docs` in your browser and use the interactive Swagger UI.

---

## 📋 Expected Behaviors

### ✅ Good Responses Should:
- Use **bold** for metric names and values
- Include units (°C, kW, dB, etc.)
- Highlight alerts at the top
- Format numbers clearly
- Provide context and interpretation

### ✅ For Historical Queries, Agent Should:
1. First call current state to see available fields
2. Use ISO 8601 durations (P1D, PT1H, etc.)
3. Choose appropriate aggregation (average, max, min)
4. Calculate dates correctly from natural language

### ✅ For "No Data" Scenarios:
- State clearly: "No data found for [metric] for [period]"
- Suggest wider date range
- Offer alternative metrics

---

## 🎯 Key Capabilities to Verify

- [x] Entity context awareness (no need to specify ID)
- [x] ISO 8601 duration format
- [x] Natural language date parsing
- [x] Multi-source data (telemetry + kpis + derived)
- [x] Smart field name extraction
- [x] Appropriate aggregation selection
- [x] Alert highlighting
- [x] Trend analysis
- [x] Comparative analysis
- [x] Error handling (no data scenarios)

---

**Pro Tip:** Start with simple queries (1-5), then move to historical (13-20), then complex (28-32). This helps you understand the agent's capabilities progressively.
