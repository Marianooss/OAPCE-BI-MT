from prescriptive_advisor import PrescriptiveAdvisor

pa = PrescriptiveAdvisor()
result = pa.generate_sales_team_recommendations()
print(f'Sales recommendations: {len(result["recommendations"])}')
if result["recommendations"]:
    for r in result["recommendations"][:3]:
        print(f'- {r["type"]}: {r["title"]}')
pa.close()
