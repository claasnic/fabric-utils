# Fabric API Identity Support Scraper

A Python web scraper that analyzes Microsoft Fabric REST API documentation to extract identity support information for each API endpoint.

## Overview

This tool scrapes the Microsoft Fabric REST API documentation and creates a comprehensive report showing which authentication methods (User vs Service Principal/Managed Identity) are supported for each API endpoint.

## Features

- **Automated Discovery**: Dynamically discovers all Fabric API endpoints from the documentation
- **Identity Support Analysis**: Extracts Microsoft Entra identity support tables from each endpoint
- **Multiple Output Formats**: Generates both console output and CSV files
- **Comprehensive Coverage**: Checks all available API endpoints across different Fabric services

## Prerequisites

### Required Python Packages

```bash
pip install playwright beautifulsoup4
```

### Install Playwright Browsers

```bash
playwright install
```

## Usage

### Basic Usage

Run the script to analyze all Fabric API endpoints:

```bash
python fabric_api_check_sp_support.py
```

### Output

The script generates:

1. **Console Output**: 
   - Progress information during scraping
   - Summary table of identity support
   - Detailed breakdown by endpoint

2. **CSV Files**:
   - `fabric_identity_support_YYYYMMDD_HHMMSS.csv` - Consolidated view
   - `fabric_identity_support_detailed_YYYYMMDD_HHMMSS.csv` - Detailed view

### Sample Output

```
Endpoint                          | User     | Service Principal & Managed Identities
--------------------------------- | -------- | --------------------------------------------------
Admin - Create Domain             | Yes      | Yes
Core - List Workspaces            | Yes      | Not supported when Git provider is AzureDevOps...
Dashboard - Get Dashboard         | Yes      | Yes
```

## CSV File Structure

### Consolidated CSV (`fabric_identity_support_*.csv`)
| Column | Description |
|--------|-------------|
| Endpoint | API endpoint name |
| URL | Documentation URL |
| User_Support | User identity support status |
| Service_Principal_Support | Service Principal/Managed Identity support status |

### Detailed CSV (`fabric_identity_support_detailed_*.csv`)
| Column | Description |
|--------|-------------|
| Endpoint | API endpoint name |
| URL | Documentation URL |
| Identity_Type | Specific identity type (User, Service Principal, etc.) |
| Support_Details | Detailed support information |

## How It Works

1. **Navigation Discovery**: Scrapes the Fabric API documentation table of contents
2. **Endpoint Extraction**: Identifies all API endpoint documentation pages
3. **Content Analysis**: Visits each page and searches for identity support tables
4. **Data Extraction**: Parses tables with `aria-label="Microsoft Entra supported identities"`
5. **Report Generation**: Consolidates findings into readable formats

## Technical Details

- **Web Scraping**: Uses Playwright for dynamic content handling
- **HTML Parsing**: BeautifulSoup for DOM manipulation
- **Async Processing**: Asynchronous operations for better performance
- **Error Handling**: Robust error handling for network issues and missing content

## Limitations

- May need updates if Microsoft changes their documentation structure

## Error Handling

The script includes comprehensive error handling for:
- Network timeouts
- Missing content
- Malformed HTML
- JavaScript loading issues

## Contributing

Feel free to submit issues or pull requests to improve the scraper's functionality or add new features.

## License

This project is for educational and analysis purposes. Please respect Microsoft's terms of service when using this tool.

## Changelog

### Latest Version
- Dynamic endpoint discovery
- CSV output generation
- Improved error handling
- Async processing for better performance

---
## Legal Considerations and License

### Terms of Use Compliance
This tool is designed for:
- **Educational and research purposes**
- **Personal development planning**
- **Non-commercial analysis of publicly available documentation**

### Usage Guidelines
- **Respect Rate Limits**: The script includes delays between requests
- **Personal Use Only**: Not intended for commercial redistribution
- **Attribution**: All scraped data belongs to Microsoft Corporation
- **No Warranty**: Use at your own risk

### Data Attribution
All API documentation and identity support information is:
- **© Microsoft Corporation**
- **Source**: https://learn.microsoft.com/en-us/rest/api/fabric/
- **Used under fair use for educational analysis**

### Disclaimer
This project is:
- **Unofficial** - Not affiliated with or endorsed by Microsoft
- **Educational** - For understanding API capabilities only
- **Respectful** - Implements reasonable delays and error handling
- **Limited Scope** - Only accesses publicly available documentation

### License
This scraping tool is provided as-is for educational purposes. Users are responsible for ensuring their use complies with:
- Microsoft's Terms of Service
- Applicable local laws
- Fair use principles

**By using this tool, you agree to use it responsibly and in compliance with all applicable terms and laws.**
