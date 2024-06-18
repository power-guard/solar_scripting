from neteco import get_neteco_api_data
from solar_edge import get_solar_edge_api_data
from leye import get_data

def run_all_apis():
    print('Starting Featching...')
    try:
        # NetEco API Calls
        print("NetEco data featching from API process start.")
        get_neteco_api_data. main()
        print("NetEco data featching from API process end.")

        # SolarEdge API Calls
        print("Solar Edge data featching from API process start.")
        get_solar_edge_api_data. main()
        print("Solar Edge data featching from API process end.")

        # l-eye API Calls
        print("L-eye data featching from API process start.")
        get_data. main()
        print("L-eye data featching from API process end.")


        # l-eye API Calls
        # Call functions from fusionsolar_api similarly

        print('All API calls completed successfully.')
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_all_apis()
