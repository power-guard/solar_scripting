from neteco import get_neteco_api_data
# from solaredge import solaredge_api
# from fusionsolar import fusionsolar_api

def run_all_apis():
    print('Starting test...')
    try:
        # NetEco API Calls
        get_neteco_api_data. main()

        # SolarEdge API Calls
        # Call functions from solaredge_api similarly

        # FusionSolar API Calls
        # Call functions from fusionsolar_api similarly

        print('All API calls completed successfully.')
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_all_apis()
