# A Qualitative and Quantitative Analysis of HTTP Benchmarking Tools

## Introduction

In this report we present a qualitative and quantitative analysis of HTTP benchmarking tools. We have selected the following tools for our analysis:

1. Wrk (https://github.com/wg/wrk)
2. Wrk2 (https://github.com/giltene/wrk2)
3. Oha (https://github.com/hatoo/oha)
4. Apache Benchmark (https://httpd.apache.org/docs/2.4/programs/ab.html)
5. Locust (https://locust.io/)
6. K6 (https://k6.io/)


## Experimental Setup

We have conducted a series of experiments on these tools using Cloudlab (https://cloudlab.us/). We have chosen the following experimental setup:

### Nodes

We have two nodes of type `c220g2` with the following specifications:

```
Type	c220g2
Class	pc
Architecture	x86_64
dom0mem	4096M
hw_cpu_bits	64
hw_cpu_cores	10
hw_cpu_hv	1
hw_cpu_sockets	2
hw_cpu_speed	2600
hw_cpu_threads	2
hw_mem_size	163840
processor	Haswell
?+disk_any	2217350
?+disk_nonsysvol	1144500
?+disk_sysvol	1072850
adminmfs_osid	FREEBSD-64-MFS-NEW
default_imageid	UBUNTU22-64-STD
default_osid	UBUNTU22-64-STD
delay_osid	FBSD-STD
diskloadmfs_osid	FRISBEE-64-MFS-NEW
jail_osid	FBSD-STD
recoverymfs_osid	RECOVERY-LINUX
```

One node is the loadgen node and the other is the server node. The loadgen node is used to run the benchmarking tools and the server node is used to run the web server.

The server node is running Nginx (https://www.nginx.com/) as the web server with default configuration. 

After every experiment, we reboot the server node to ensure that the server is in a clean state.

For every experiment, we measure the following metrics:

1. CPU Utilization (in %)
2. Memory Utilization (in KB)
3. Bandwidth Utilization (in KB/s)
4. Bandwidth Utilization (in %)
5. Open Sockets

## Background

HTTP benchmarking tools are used to measure the performance of web servers and applications by simulating a large number of concurrent users making requests to the server. These tools are commonly used to test the scalability and reliability of web applications under different load conditions. They can help identify performance bottlenecks, optimize resource usage, and improve the overall user experience. Each tool has its own strengths and weaknesses, and is suited for different types of testing scenarios. In this report, we will compare the features, capabilities, and performance of the selected tools. 

Through our experiments we have observed the following configurations affect the performance of the tools, we will use these configurations to present a quantitative analysis of the tools:

1. **Number of connections**: The number of concurrent connections that the tool will make to the server. This can range from a few connections to thousands of connections. Each tool has its own way of specifying the number of connections. Each connection defines a single user session. 

2. **Duration**: The duration for which the tool will run the benchmark. This can range from a few seconds to several hours. 

3. **Keep-alive**: Whether the tool will reuse the same connection for multiple requests or open a new connection for each request. 

4. **Request Rate**: The rate at which the tool should send requests to the server. This can be specified in requests per second (RPS) or requests per minute (RPM). Some tools allow you to configure this parameter, whereas others do not.

5. **Multi-threading/Multi-processing**: Whether the tool uses multiple threads or processes to send requests to the server. 

Here's is a list showing each evaluated tool and the configurations it supports:

| Tool              | Number of Connections | Duration | Disable Keep-alive | Request Rate | Multi-threading/Multi-processing |
|-------------------|-----------------------|----------|--------------------|--------------|----------------------------------|
| Wrk               | Yes                   | Yes      | No                 | No           | Yes (Multi-Threading)            |
| Wrk2              | Yes                   | Yes      | No                 | Yes          | Yes (Multi-Threading)            |
| Oha               | Yes                   | Yes      | Yes                | Yes          | Yes (Multi-Threading)            |
| Apache Benchmark  | Yes                   | Yes      | No                 | Yes          | No                               |
| Locust            | Yes                   | Yes      | Yes                | Yes          | Yes (Multi-Processing)           |
| K6                | Yes                   | Yes      | Yes                | Yes          | Yes (Multi-Threading)            |


### Tools Overview

#### Wrk

Wrk is a benchmarking tool written in C that is designed for testing HTTP servers. 

Here are some of the key features of Wrk:
1. **Supports Multi-Threading**: Wrk uses multiple threads to manage connections and send requests to the server. This allows it to simulate a large number of concurrent users.
2. **Connections Keep-alive**: Wrk only supports keep-alive connections, which means that it reuses the same connection for multiple requests.
3. **Lua Scripting**: Wrk allows you to write Lua scripts to customize the request generation process. This can be useful for testing complex scenarios.
4. **Metrics**: Wrk provides the following metrics for each benchmark: 
    - **Thread Metrics**:
        - Latency: Average, Stdev, Max, +/- Stdev
        - Req/Sec: Average, Stdev, Max, +/- Stdev
    - **Latency Distribution**:
        - 50%, 75%, 90%, 99%
    - **Number of requests**: Total
    - **Requests/sec**: Total number of requests / duration
    - **Transfer/sec**: Total number of bytes transferred / duration
5. **Configuration**: Wrk allows configuring the following parameters:
    - **Number of connections**: The total number of connections which will be distributed among threads.
    - **Duration**: The duration for which the benchmark will run.
    - **Number of threads**: The number of threads that will be used to send requests.
    - **Script**: The Lua script that will be used to generate requests.
    - **Timeout**: The timeout for each request.
    - **Headers**: The headers that will be sent with each request.

Here is a sample output of running wrk:
```
Running 1m test @ http://192.168.1.2/
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   101.68us   25.37us   5.50ms   86.67%
    Req/Sec    94.44k     6.66k  102.67k    91.18%
  Latency Distribution
     50%   96.00us
     75%  109.00us
     90%  128.00us
     99%  190.00us
  5646128 requests in 1.00m, 4.52GB read
Requests/sec:  93945.84
Transfer/sec:     76.96MB
```

Here are the details of the configurations we used to evaluate Wrk: 

|exp_name|threads|connections|duration|rps|avg_cpu                           |avg_memory                    |avg_bandwidth|avg_bandwidth_utilization|avg_open_sockets  |
|--------|-------|-----------|--------|---|----------------------------------|------------------------------|-------------|-------------------------|------------------|
|wrk-1   |1      |10         |60      |93945.84|75.15                             |1652.0833333333333            |91397.05833333333|7.140000000000001        |7.5               |
|wrk-2   |1      |10         |120     |93070.32|76.20416666666667                 |1735.5                        |90296.0025   |7.054583333333333        |8.416666666666666 |
|wrk-3   |5      |10         |120     |85145.22|207.61666666666667                |1818.1666666666667            |82574.47833333333|6.452083333333333        |8.375             |
|wrk-4   |5      |100        |120     |175737.13|287.8333333333333                 |2395.4583333333335            |170420.81666666668|13.314583333333331       |95.41666666666667 |
|wrk-5   |5      |1000       |120     |178971.44|300.2916666666667                 |7538.541666666667             |173550.69166666668|13.558333333333332       |968.6666666666666 |
|wrk-6   |10     |1000       |480     |179004.74|487.8709677419355                 |8349.913978494624             |178944.09354838709|13.980645161290319       |982.7096774193549 |
|wrk-7   |20     |1000       |480     |178694.46|637.4967741935484                 |9743.52688172043              |178613.7752688172|13.954516129032255       |982.8602150537635 |
|wrk-8   |30     |1000       |480     |178076.82|675.7548387096774                 |11383.709677419354            |177931.23978494626|13.900860215053765       |972.7311827956989 |
|wrk-9   |30     |1000       |600     |179698.59|634.1060344827587                 |11385.637931034482            |180018.06293103448|14.063793103448276       |974.8275862068965 |
|wrk-10  |10     |600        |600     |180192.37|487.9853448275863                 |5964.6551724137935            |180561.28275862068|14.106724137931035       |588.7413793103449 |

Here are some graphs that show the performance of wrk against the different configurations: 

**RPS vs Average CPU Utilization**

![RPS vs CPU Utilization](plots/wrk_rps_vs_avg_cpu.png)

**RPS vs Average Memory Utilization**

![RPS vs Memory Utilization](plots/wrk_rps_vs_avg_mem.png)

*Analysis*: 

Wrk-1 experiment runs wrk as as a single thread with 10 connections for 60 seconds. The average CPU utilization is only 75% giving an RPS of about 93k. Wrk-2 is the similar configuration running for 120 seconds - the RPS and memory in this case is not affected. Similarly, Wrk-8 and Wrk-9 have similar RPS and memory utilizations. 

![Comparisons](plots/wrk-1_wrk-2_comparison.png)

The bandwidth utilization is almost consistent throughout the duration of the experiment. This can be attributed to the fact that wrk keeps the connections alive and reuses them for multiple requests. The number of open sockets fluctuates between 5 and 10. 

The experiments wrk-3, wrk-4, and wrk-5 show the results of increasing the number of connections to 10, 100, and 1000 while keeping the number of threads constant at 5. 

![Comparisons](plots/wrk-3_wrk-4_wrk-5_comparison.png)

Thought the number of connections differ by a factor of 10 between wrk-4 and wrk-5, they both have similar RPS, CPU, and Bandwidth Utilization. The Memory Utilization and Open Sockets are higher in wrk-5 because of the increased number of connections. 

The experiments wrk-6, wrk-7, and wrk-8 show the results of increasing the number of threads to 10, 20, and 30 while keeping the number of connections constant at 1000 and the duration at 480 seconds. 

![Comparisons](plots/wrk-6_wrk-7_wrk-8_comparison.png)

We were able to get the best RPS in experiment wrk-10 with 180k RPS.

![Comparisons](plots/wrk-10_comparison.png)


