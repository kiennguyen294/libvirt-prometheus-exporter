collect RAM use
lvirt_domain_mem_in_use_byte/(lvirt_domain_info_memory_available_byte)*100

collect CPU use
irate(lvirt_domain_info_cpu_time_total[5m])*100
