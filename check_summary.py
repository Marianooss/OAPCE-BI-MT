from prescriptive_advisor import PrescriptiveAdvisor

pa = PrescriptiveAdvisor()
result = pa.get_recommendations_summary()
print(f'Summary success: {result.get("success")}')
print(f'Total recommendations: {result.get("total_recommendations")}')
print(f'Top recommendations count: {len(result.get("top_recommendations", []))}')

if result.get("top_recommendations"):
    for r in result["top_recommendations"][:3]:
        print(f'- {r.get("title")}')

pa.close()
