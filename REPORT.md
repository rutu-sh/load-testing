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

1. Number of connections: The number of concurrent connections that the tool will make to the server. This can range from a few connections to thousands of connections. Each tool has its own way of specifying the number of connections. Each connection defines a single user session. 

2. Duration: The duration for which the tool will run the benchmark. This can range from a few seconds to several hours. 

3. Keep-alive: Whether the tool will reuse the same connection for multiple requests or open a new connection for each request. 

4. Request Rate: The rate at which the tool should send requests to the server. This can be specified in requests per second (RPS) or requests per minute (RPM). Some tools allow you to configure this parameter, whereas others do not.

5. Multi-threading/Multi-processing: Whether the tool uses multiple threads or processes to send requests to the server. 

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