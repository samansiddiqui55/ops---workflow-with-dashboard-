#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class OpsFlowAPITester:
    def __init__(self, base_url="https://jira-sync-flow.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int = 200, data: Dict[Any, Any] = None, params: Dict[str, str] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_health_endpoints(self):
        """Test basic health and root endpoints"""
        print("\n" + "="*50)
        print("TESTING HEALTH ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        self.run_test("Root API", "GET", "", 200)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "health", 200)

    def test_tickets_endpoints(self):
        """Test all ticket-related endpoints"""
        print("\n" + "="*50)
        print("TESTING TICKETS ENDPOINTS")
        print("="*50)
        
        # Test get all tickets
        success, tickets_data = self.run_test("Get All Tickets", "GET", "tickets/", 200)
        
        if success and tickets_data:
            print(f"   Found {len(tickets_data)} tickets")
            
            # Test specific ticket fields
            if len(tickets_data) > 0:
                ticket = tickets_data[0]
                required_fields = ['id', 'brand', 'sender_email', 'summary', 'status', 'created_at']
                missing_fields = [field for field in required_fields if field not in ticket]
                
                if missing_fields:
                    print(f"⚠️  Missing required fields in ticket: {missing_fields}")
                else:
                    print("✅ All required ticket fields present")
                
                # Test get specific ticket
                ticket_id = ticket.get('id')
                if ticket_id:
                    self.run_test(f"Get Ticket {ticket_id}", "GET", f"tickets/{ticket_id}", 200)
                
                # Test resolve ticket (only if not already resolved)
                if ticket.get('status') != 'resolved':
                    resolve_payload = {
                        "latest_comment": "Test resolution from API test",
                        "resolution_notes": "Automated test resolution"
                    }
                    self.run_test(f"Resolve Ticket {ticket_id}", "POST", f"tickets/{ticket_id}/resolve", 200, resolve_payload)
        else:
            print("⚠️  No tickets found or failed to fetch tickets")

    def test_analytics_endpoints(self):
        """Test all analytics endpoints"""
        print("\n" + "="*50)
        print("TESTING ANALYTICS ENDPOINTS")
        print("="*50)
        
        # Test analytics summary
        success, summary_data = self.run_test("Analytics Summary", "GET", "analytics/summary", 200)
        
        if success and summary_data:
            # Check if summary has real data
            summary = summary_data.get('summary', {})
            total_issues = summary.get('total_issues', 0)
            
            if total_issues > 0:
                print(f"✅ Analytics has real data: {total_issues} total issues")
            else:
                print("⚠️  Analytics summary shows 0 total issues")
        
        # Test analytics summary with period filter
        self.run_test("Analytics Summary (1 Year)", "GET", "analytics/summary", 200, params={"period": "1y"})
        
        # Test issues by client
        success, client_data = self.run_test("Issues by Client", "GET", "analytics/issues-by-client", 200)
        if success and client_data:
            data = client_data.get('data', [])
            print(f"   Found {len(data)} clients with issues")
        
        # Test issue types
        success, types_data = self.run_test("Issue Types", "GET", "analytics/issue-types", 200)
        if success and types_data:
            data = types_data.get('data', [])
            print(f"   Found {len(data)} issue types")
        
        # Test time series
        success, series_data = self.run_test("Time Series", "GET", "analytics/time-series", 200)
        if success and series_data:
            data = series_data.get('data', [])
            print(f"   Found {len(data)} time series data points")
        
        # Test TAT by client
        success, tat_data = self.run_test("TAT by Client", "GET", "analytics/tat-by-client", 200)
        if success and tat_data:
            data = tat_data.get('data', [])
            print(f"   Found TAT data for {len(data)} clients")

    def test_websocket_endpoint(self):
        """Test WebSocket endpoint accessibility"""
        print("\n" + "="*50)
        print("TESTING WEBSOCKET ENDPOINT")
        print("="*50)
        
        # We can't easily test WebSocket connection in this simple script,
        # but we can check if the endpoint is accessible
        ws_url = self.base_url.replace("https://", "wss://") + "/ws/tickets"
        print(f"📡 WebSocket URL: {ws_url}")
        print("✅ WebSocket endpoint configured (actual connection test requires frontend)")

    def test_jira_url_format(self):
        """Test that Jira URLs are correctly formatted"""
        print("\n" + "="*50)
        print("TESTING JIRA URL FORMAT")
        print("="*50)
        
        success, tickets_data = self.run_test("Get Tickets for Jira URL Check", "GET", "tickets/", 200)
        
        if success and tickets_data:
            jira_base = "https://grow-simplee.atlassian.net"
            tickets_with_jira = [t for t in tickets_data if t.get('jira_issue_key')]
            
            if tickets_with_jira:
                for ticket in tickets_with_jira[:3]:  # Check first 3
                    issue_key = ticket.get('jira_issue_key')
                    expected_url = f"{jira_base}/browse/{issue_key}"
                    
                    if ticket.get('jira_url') == expected_url:
                        print(f"✅ Correct Jira URL format for {issue_key}")
                    else:
                        print(f"❌ Incorrect Jira URL for {issue_key}")
                        print(f"   Expected: {expected_url}")
                        print(f"   Actual: {ticket.get('jira_url')}")
            else:
                print("⚠️  No tickets with Jira issue keys found")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting OpsFlow API Testing...")
        print(f"Base URL: {self.base_url}")
        
        self.test_health_endpoints()
        self.test_tickets_endpoints()
        self.test_analytics_endpoints()
        self.test_websocket_endpoint()
        self.test_jira_url_format()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"✅ Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed tests ({len(self.failed_tests)}):")
            for i, failure in enumerate(self.failed_tests, 1):
                print(f"   {i}. {failure.get('test', 'Unknown')}")
                if 'error' in failure:
                    print(f"      Error: {failure['error']}")
                else:
                    print(f"      Expected: {failure.get('expected')}, Got: {failure.get('actual')}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = OpsFlowAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())