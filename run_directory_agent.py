import os
import sys
# Ensure the current directory is in path
sys.path.append(os.getcwd())

from mafisa_insights.directory_agent import DirectoryAgent

def main():
    print("Initializing Directory Enrichment Agent...")
    agent = DirectoryAgent()

    # Run scraping with a small limit for demo
    agent.scrape_directory(limit=5)

    # Save data
    data_path = os.path.join("mafisa_insights", "data", "directory_listings.json")
    # Ensure directory exists
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    agent.save_data(data_path)

    # Generate Report
    report_path = "Weekly_Insights_Report.md"
    agent.generate_insights_report(report_path)

    print("Agent workflow complete.")

if __name__ == "__main__":
    main()
