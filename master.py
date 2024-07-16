from neteco import get_neteco_api_data
from solar_edge import get_solar_edge_api_data
from leye import leye_get_data
from ecolive import eco_live_get_data
from tabuchi_cloud import tabuchi_cloud_get_data
from fusion_solar import fusion_solar_get_data
from fusion_solar_automation import get_fusion_solar

def run_all_apis():
    print('Starting Featching...')
    try:
        print("-------------------------------------------------------------------------\n"
              "-----------------------------START---------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        # NetEco API Calls
        print("NetEco data featching from API process start.")
        get_neteco_api_data.main()
        print("NetEco data featching from API process end.")

        print("-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        # SolarEdge API Calls
        print("Solar Edge data featching from API process start.")
        get_solar_edge_api_data.main()
        print("Solar Edge data featching from API process end.")

        print("-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        # Ecolive API Calls
        print("Ecolive data featching from API process start.")
        eco_live_get_data.main()
        print("Ecolive data featching from API process end.")

        print("-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        # tabuchi_cloud API Calls
        print("Tabuchi Cloud data featching from API process start.")
        tabuchi_cloud_get_data.main()
        print("Tabuchi Cloud data featching from API process end.")

        print("-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        # Fusion Solar API Calls
        print("Fusion Solar data featching from API process start.")
        fusion_solar_get_data.main()
        print("Fusion Solar data featching from API process end.")

        print("-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        # SolarEdge API Calls
        print("SolarEdge data fetching from API process start.")
        get_fusion_solar.main()
        print("SolarEdge data fetching from API process end.")

        print("-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        # l-eye API Calls
        print("L-eye data featching from API process start.")
        leye_get_data.main()
        print("L-eye data featching from API process end.")

        print("-------------------------------------------------------------------------\n"
              "-------------------------------END---------------------------------------\n"
              "-------------------------------------------------------------------------\n"  )

        

        # l-eye API Calls
        # Call functions from fusionsolar_api similarly

        print('All API calls completed successfully.')
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_all_apis()
