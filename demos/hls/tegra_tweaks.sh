#!/bin/bash

sysctl -w net.core.rmem_max=1048576
sysctl -w net.core.rmem_default=1048576
sysctl -w net.core.wmem_max=1048576
sysctl -w net.core.wmem_default=1048576
sysctl -w net.ipv4.udp_mem="8388608 12582912 16777216"
sysctl -w net.ipv4.tcp_rmem="10240 87380 12582912"
sysctl -w net.ipv4.tcp_wmem="10240 87380 12582912"
#sysctl -w net.ipv4.tcp_congestion_control=htcp
sysctl -w net.ipv4.tcp_slow_start_after_idle=0

echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo userspace > /sys/devices/system/cpu/cpuquiet/current_governor
echo 1 > /sys/devices/system/cpu/cpu1/online
