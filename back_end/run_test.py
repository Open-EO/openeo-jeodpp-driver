from run import run_job

def main():
    tileindex = None
    tiletotal = None
    # process_graph = "tests/process_graphs/zonal_statistics_timeseries_test.json"
    #process_graph = "tests/process_graphs/zonal_statistics_test.json"
    #process_graph = "tests/process_graphs/zonal_statistics.json"
    #process_graph = "tests/process_graphs/zonal_statistics_timeseries.json"
    #process_graph = "tests/process_graphs/zonal_statistics_timeseries_geometry.json"
    #process_graph = "tests/process_graphs/zonal_statistics_timeseries_mgrs.json"
    #process_graph = "tests/process_graphs/zonal_statistics_timeseries_file.json"
    #process_graph = "tests/process_graphs/zonal_statistics_timeseries_ndvi_file.json"
    #process_graph = "tests/process_graphs/ndvi_masked_timeseries.json"
    #process_graph = "tests/process_graphs/ndvi_masked_timeseries_udf.json"
    #process_graph = "tests/process_graphs/zonal_statistics_timeseries_ndvi_file_mask.json"
    #process_graph = "tests/process_graphs/zonal_statistics_timeseries_ndvi_udf.json"
    #process_graph = "tests/process_graphs/jrc_usecase5_noudf.json"
    #process_graph = "tests/process_graphs/JRC_job.json"
    #process_graph = "tests/process_graphs/jrc_uc1_pol.json"
    #process_graph = "tests/process_graphs/jrc_uc1_temp.json"
    #process_graph = "tests/process_graphs/jrc_usecase5_udf.json"
    process_graph = "tests/process_graphs/jrc_usecase5_noudf.json"
    #process_graph = "/home/kempepi/openeo-usecases/evi_d22_usecase/D35/jrc.json"
    #process_graph = "/home/kempepi/openeo-usecases/jrc_agriculture_monitoring_usecase/D35/jrc_noudf.json"
    #process_graph = "/home/kempepi/openeo-usecases/jrc_agriculture_monitoring_usecase/D35/jrc_noudf.json"
    #process_graph = "/home/kempepi/openeo-usecases/jrc_agriculture_monitoring_usecase/D35/jrc_noudf.json"
    run_job_graph(process_graph, tileindex = tileindex, tiletotal = tiletotal)

if __name__ == "__main__":
    main()
