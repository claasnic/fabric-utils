import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv
from io import StringIO
from datetime import datetime

async def scrape_fabric_menu():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # First, get all API endpoints
            await page.goto("https://learn.microsoft.com/en-us/rest/api/fabric/articles/")
            await page.wait_for_load_state('networkidle')
            
            # Expand all sections
            try:
                await page.wait_for_selector('ul[role="tree"]', timeout=10000)
                
                for attempt in range(5):
                    expandable_items = await page.query_selector_all('ul[role="tree"] [aria-expanded="false"]')
                    print(f"Expansion attempt {attempt + 1}: Found {len(expandable_items)} expandable items")
                    
                    if len(expandable_items) == 0:
                        break
                    
                    for item in expandable_items:
                        try:
                            await item.click(timeout=500)
                            await page.wait_for_timeout(30)
                        except:
                            continue
                    
                    await page.wait_for_timeout(1000)
                        
            except Exception as e:
                print(f"Expansion failed: {e}")
            
            await page.wait_for_timeout(2000)
            
            # Get all API endpoints
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            toc = soup.find('ul', attrs={'role': 'tree'})
            
            if not toc:
                print("TOC not found")
                return
            
            all_api_endpoints = {}
            
            for link in toc.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if (href and text and 
                    '/rest/api/fabric/' in href and
                    text not in ['Microsoft Fabric REST API documentation']):
                    
                    if href.startswith('/'):
                        href = f"https://learn.microsoft.com{href}"
                    
                    all_api_endpoints[text] = href
            
            print(f"Found {len(all_api_endpoints)} API endpoints to check")
            
            # Now visit each endpoint and look for the identity support table
            identity_support_data = []
            
            for i, (endpoint_name, endpoint_url) in enumerate(all_api_endpoints.items()):
                print(f"Checking {i+1}/{len(all_api_endpoints)}: {endpoint_name}")
                
                try:
                    await page.goto(endpoint_url, timeout=30000)
                    await page.wait_for_load_state('networkidle', timeout=15000)
                    
                    # Get page content and search for the identity table
                    page_content = await page.content()
                    page_soup = BeautifulSoup(page_content, 'html.parser')
                    
                    # Look for table with aria-label="Microsoft Entra supported identities"
                    identity_table = page_soup.find('table', attrs={'aria-label': 'Microsoft Entra supported identities'})
                    
                    if identity_table:
                        # Extract table data
                        rows = identity_table.find_all('tr')
                        
                        if len(rows) >= 2:  # Header + at least one data row
                            # Skip header row, process data rows
                            for row in rows[1:]:
                                cells = row.find_all(['td', 'th'])
                                if len(cells) >= 2:
                                    identity_type = cells[0].get_text(strip=True)
                                    support_info = cells[1].get_text(strip=True)
                                    
                                    identity_support_data.append({
                                        'Endpoint': endpoint_name,
                                        'URL': endpoint_url,
                                        'Identity': identity_type,
                                        'Support': support_info
                                    })
                    
                    # Small delay between requests
                    await page.wait_for_timeout(500)
                    
                except Exception as e:
                    print(f"  Error checking {endpoint_name}: {str(e)[:100]}...")
                    continue
            
            # Output results
            if identity_support_data:
                print(f"\n✓ Found identity support information for {len(set(item['Endpoint'] for item in identity_support_data))} endpoints")
                
                # Create a consolidated table
                print(f"\n{'='*120}")
                print("MICROSOFT ENTRA IDENTITY SUPPORT TABLE")
                print(f"{'='*120}")
                
                # Group by endpoint for better display
                by_endpoint = {}
                for item in identity_support_data:
                    endpoint = item['Endpoint']
                    if endpoint not in by_endpoint:
                        by_endpoint[endpoint] = []
                    by_endpoint[endpoint].append(item)
                
                # Print table header
                print(f"{'Endpoint':<40} | {'User':<8} | {'Service Principal & Managed Identities'}")
                print(f"{'-'*40} | {'-'*8} | {'-'*50}")
                
                # Prepare CSV data
                csv_data = []
                
                # Print data and prepare CSV
                for endpoint in sorted(by_endpoint.keys()):
                    items = by_endpoint[endpoint]
                    
                    user_support = "N/A"
                    sp_support = "N/A"
                    endpoint_url = items[0]['URL']
                    
                    for item in items:
                        if "User" in item['Identity']:
                            user_support = item['Support']
                        elif "Service principal" in item['Identity'] or "Managed identities" in item['Identity']:
                            sp_support = item['Support']
                    
                    # Add to CSV data
                    csv_data.append({
                        'Endpoint': endpoint,
                        'URL': endpoint_url,
                        'User_Support': user_support,
                        'Service_Principal_Support': sp_support
                    })
                    
                    # Truncate long text for console display
                    endpoint_display = endpoint[:37] + "..." if len(endpoint) > 40 else endpoint
                    user_display = user_support[:5] + "..." if len(user_support) > 8 else user_support
                    sp_display = sp_support[:47] + "..." if len(sp_support) > 50 else sp_support
                    
                    print(f"{endpoint_display:<40} | {user_display:<8} | {sp_display}")
                
                # Write to CSV file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"fabric_identity_support_{timestamp}.csv"
                
                with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Endpoint', 'URL', 'User_Support', 'Service_Principal_Support']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write header
                    writer.writeheader()
                    
                    # Write data
                    for row in csv_data:
                        writer.writerow(row)
                
                print(f"\n✓ CSV file saved as: {csv_filename}")
                print(f"  Contains {len(csv_data)} endpoints with identity support information")
                
                # Also create a detailed CSV with all identity types
                detailed_csv_filename = f"fabric_identity_support_detailed_{timestamp}.csv"
                
                with open(detailed_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Endpoint', 'URL', 'Identity_Type', 'Support_Details']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write header
                    writer.writeheader()
                    
                    # Write detailed data
                    for item in identity_support_data:
                        writer.writerow({
                            'Endpoint': item['Endpoint'],
                            'URL': item['URL'],
                            'Identity_Type': item['Identity'],
                            'Support_Details': item['Support']
                        })
                
                print(f"✓ Detailed CSV file saved as: {detailed_csv_filename}")
                print(f"  Contains {len(identity_support_data)} individual identity support entries")
                
                # Also save detailed data to console
                print(f"\n{'='*120}")
                print("DETAILED IDENTITY SUPPORT DATA:")
                print(f"{'='*120}")
                
                for endpoint in sorted(by_endpoint.keys()):
                    print(f"\n{endpoint}:")
                    print(f"  URL: {by_endpoint[endpoint][0]['URL']}")
                    for item in by_endpoint[endpoint]:
                        print(f"  {item['Identity']}: {item['Support']}")
                        
            else:
                print("No identity support tables found")
                
        except Exception as e:
            print(f"Script error: {e}")
        finally:
            await browser.close()

asyncio.run(scrape_fabric_menu())