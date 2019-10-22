import sys

import libvirt
from prometheus_client.core import GaugeMetricFamily
import six


def parse_net(stat):
    if 'net.count' not in stat:
        return []
    net_stat = []
    for i in range(int(stat['net.count'])):
        current_stat = {
            'name': stat['net.' + str(i) + '.name'],
            'rx_bytes': stat['net.' + str(i) + '.rx.bytes'],
            'rx_pkts': stat['net.' + str(i) + '.rx.pkts'],
            'rx_errors': stat['net.' + str(i) + '.rx.errs'],
            'rx_drops': stat['net.' + str(i) + '.rx.drop'],
            'tx_bytes': stat['net.' + str(i) + '.tx.bytes'],
            'tx_pkts': stat['net.' + str(i) + '.tx.pkts'],
            'tx_errors': stat['net.' + str(i) + '.tx.errs'],
            'tx_drops': stat['net.' + str(i) + '.tx.drop']
        }
        net_stat.append(current_stat)
    return net_stat


def parse_blk(stat):
    if 'block.count' not in stat or stat['state.state'] != 1:
        return []
    blk_stat = []
    for i in range(int(stat['block.count'])):
        if stat['block.%s.name' %i] == 'hda':
            continue
        current_stat = {
            'name': stat.get('block.' + str(i) + '.name', ''),
            'path': stat.get('block.' + str(i) + '.path', ''),
            'allocation': stat.get('block.' + str(i) + '.allocation', ''),
            'capacity': stat.get('block.' + str(i) + '.capacity', ''),
            'physical': stat.get('block.' + str(i) + '.physical', ''),
            'read_requests': stat.get('block.' + str(i) + '.rd.reqs', ''),
            'read_bytes': stat.get('block.' + str(i) + '.rd.bytes', ''),
            'read_seconds': stat.get('block.' + str(i) + '.rd.times', ''),
            'write_requests': stat.get('block.' + str(i) + '.wr.reqs', ''),
            'write_bytes': stat.get('block.' + str(i) + '.wr.bytes', ''),
            'write_seconds': stat.get('block.' + str(i) + '.wr.times', ''),
            'flush_requests': stat.get('block.' + str(i) + '.fl.reqs', ''),
            'flush_seconds': stat.get('block.' + str(i) + '.fl.times', '')
        }
        blk_stat.append(current_stat)
    return blk_stat


class LibvirtCollector(object):

    def __init__(self, uri):
        conn = libvirt.open(uri)

        if conn is None:
            print('Failed to open connection to ' + uri, file = sys.stderr)
        else:
            print('Successfully connected to ' + uri)

        self.uri = uri
        self.conn = conn

    def collect(self):
        stats = self.conn.getAllDomainStats()
        state = GaugeMetricFamily(
            'lvirt_domain_info_state',
            'Current state for the domain.',
            labels=['name', 'id'])
        vcpus = GaugeMetricFamily(
            'lvirt_domain_info_vcpus',
            'Number of virtual CPUs for the domain.',
            labels=['name', 'id'])
        cpu_time = GaugeMetricFamily(
            'lvirt_domain_info_cpu_time_total',
            'Amount of CPU time used by the domain, in seconds.',
            labels=['name', 'id'])
        mem_max = GaugeMetricFamily(
            'lvirt_domain_info_maximum_memory_bytes',
            'Maximum allowed memory of the domain, in bytes.',
            labels=['name', 'id'])
        mem_curr = GaugeMetricFamily(
            'lvirt_domain_info_memory_current_bytes',
            'Memory usage of the domain, in bytes.',
            labels=['name', 'id'])
        mem_available = GaugeMetricFamily(
            'lvirt_domain_info_memory_available_byte',
            'Memory available of the domain in byte',
            labels=['name', 'id'])
        mem_unused = GaugeMetricFamily(
            'lvirt_domain_info_memory_unused_byte',
            'Memory unused of the domain in byte',
            labels=['name', 'id'])
        mem_usable = GaugeMetricFamily(
            'lvirt_domain_info_memory_usable_byte',
            'Memory usable of the domain in byte',
            labels=['name', 'id']
        )
        mem_in_used = GaugeMetricFamily(
	        'lvirt_domain_mem_in_use_byte',
	        'Memory in used of domain in byte',
	        labels=['name', 'id']
        )
        net_receive_bytes = GaugeMetricFamily(
            'lvirt_domain_interface_stats_receive_bytes_total',
            'Number of bytes received on a network interface, in bytes.',
            labels=['name', 'id', 'interface'])
        net_receive_packets = GaugeMetricFamily(
            'lvirt_domain_interface_stats_receive_bytes_total',
            'Number of packets received on a network interface.',
            labels=['name', 'id', 'interface'])
        net_receive_errors = GaugeMetricFamily(
            'lvirt_domain_interface_stats_receive_errors_total',
            'Number of packet receive errors on a network interface.',
            labels=['name', 'id', 'interface'])
        net_receive_drops = GaugeMetricFamily(
            'lvirt_domain_interface_stats_receive_drops_total',
            'Number of packet receive drops on a network interface.',
            labels=['name', 'id', 'interface'])
        net_transmit_bytes = GaugeMetricFamily(
            'lvirt_domain_interface_stats_transmit_bytes_total',
            'Number of bytes transmitted on a network interface, in bytes.',
            labels=['name', 'id', 'interface'])
        net_transmit_packets = GaugeMetricFamily(
            'lvirt_domain_interface_stats_transmit_bytes_total',
            'Number of packets transmitted on a network interface..',
            labels=['name', 'id', 'interface'])
        net_transmit_errors = GaugeMetricFamily(
            'lvirt_domain_interface_stats_transmit_errors_total',
            'Number of packet transmit errors on a network interface.',
            labels=['name', 'id', 'interface'])
        net_transmit_drops = GaugeMetricFamily(
            'lvirt_domain_interface_stats_transmit_drops_total',
            'Number of packet transmit drops on a network interface.',
            labels=['name', 'id', 'interface'])

        blk_read_request = GaugeMetricFamily(
            'lvirt_domain_block_stats_read_requests_total',
            'Number of read requests from a block device.',
            labels=['name', 'id', 'device', 'path'])
        blk_read_bytes = GaugeMetricFamily(
            'lvirt_domain_block_stats_read_bytes_total',
            'Number of bytes read from a block device, in bytes.',
            labels=['name', 'id', 'device', 'path'])
        blk_read_seconds = GaugeMetricFamily(
            'lvirt_domain_block_stats_read_seconds_total',
            'Amount of time spent reading from a block device, in seconds.',
            labels=['name', 'id', 'device', 'path'])
        blk_write_request = GaugeMetricFamily(
            'lvirt_domain_block_stats_write_requests_total',
            'Number of write requests from a block device.',
            labels=['name', 'id', 'device', 'path'])
        blk_write_bytes = GaugeMetricFamily(
            'lvirt_domain_block_stats_write_bytes_total',
            'Number of bytes written from a block device, in bytes.',
            labels=['name', 'id', 'device', 'path'])
        blk_write_seconds = GaugeMetricFamily(
            'lvirt_domain_block_stats_write_seconds_total',
            'Amount of time spent writing from a block device, in seconds.',
            labels=['name', 'id', 'device', 'path'])
        blk_flush_requests = GaugeMetricFamily(
            'lvirt_domain_block_stats_flush_requests_total',
            'Number of flush requests from a block device.',
            labels=['name', 'id', 'device', 'path'])
        blk_flush_seconds = GaugeMetricFamily(
            'lvirt_domain_block_stats_flush_seconds_total',
            'Amount of time spent flushing of a block device, in seconds.',
            labels=['name', 'id', 'device', 'path'])

        for domain, stat in stats:
           # if domain.UUIDString() != '09a15ea6-9909-41fc-9943-5f99da4b33f7':
           #     continue
            base_label = [domain.name(), domain.UUIDString()]
            state.add_metric(base_label, stat['state.state'])
            vcpus.add_metric(base_label, stat['vcpu.current'])

            current_cpus = stat.get('vcpu.current')

            mem_max.add_metric(base_label, stat['balloon.maximum'])

            if stat['state.state'] == 1:
                cpu_time_tmp = 0
                for vcpu in six.moves.range(stat['vcpu.maximum']):
                    try:
                        cpu_time_tmp += (stat.get('vcpu.%s.time' % vcpu) +
                                     stat.get('vcpu.%s.wait' % vcpu))
                        current_cpus -= 1
                    except TypeError:
                        pass
                if current_cpus:
                    cpu_time_tmp = stat.get('cpu.time')
                cpu_time_tmp = cpu_time_tmp / (1000000000 * stat['vcpu.maximum']) # 1000000000 is 1GHz, cp_time is clock rate

                cpu_time.add_metric(base_label, cpu_time_tmp)
                mem_curr.add_metric(base_label, stat['balloon.current'])

                if 'usable' in domain.memoryStats() and 'available' in domain.memoryStats():
                    mem_available.add_metric(base_label, stat['balloon.available'])
                    mem_usable.add_metric(base_label, stat['balloon.usable'])
                    mem_in_used.add_metric(base_label, stat['balloon.available'] - stat['balloon.usable'])

                elif 'unused' in domain.memoryStats() and 'available' in domain.memoryStats():
                    mem_available.add_metric(base_label, stat['balloon.available'])
                    mem_unused.add_metric(base_label, stat['balloon.unused'])
                    mem_in_used.add_metric(base_label, stat['balloon.available'] - stat['balloon.unused'])

            for net in parse_net(stat):
                net_label = [domain.name(), domain.UUIDString(), net['name']]
                net_receive_bytes.add_metric(net_label, net['rx_bytes'])
                net_receive_packets.add_metric(net_label, net['rx_pkts'])
                net_receive_drops.add_metric(net_label, net['rx_drops'])
                net_receive_errors.add_metric(net_label, net['rx_errors'])
                net_transmit_bytes.add_metric(net_label, net['tx_bytes'])
                net_transmit_packets.add_metric(net_label, net['tx_pkts'])
                net_transmit_errors.add_metric(net_label, net['tx_errors'])
                net_transmit_drops.add_metric(net_label, net['tx_drops'])

            for blk in parse_blk(stat):
                blk_label = [domain.name(), domain.UUIDString(),
                             blk['name'], blk['path']]
                blk_read_bytes.add_metric(blk_label, blk['read_bytes'])
                blk_read_request.add_metric(blk_label, blk['read_requests'])
                blk_read_seconds.add_metric(blk_label, blk['read_seconds'])
                blk_write_bytes.add_metric(blk_label, blk['write_bytes'])
                blk_write_request.add_metric(blk_label, blk['write_requests'])
                blk_write_seconds.add_metric(blk_label, blk['write_seconds'])
                blk_flush_requests.add_metric(blk_label, blk['flush_requests'])
                blk_flush_seconds.add_metric(blk_label, blk['flush_seconds'])

        yield state
        yield vcpus
        yield cpu_time
        yield mem_max
        yield mem_curr
        yield mem_available
        yield mem_unused
        yield mem_in_used
        yield net_receive_bytes
        yield net_receive_packets
        yield net_receive_errors
        yield net_receive_drops
        yield net_transmit_bytes
        yield net_transmit_packets
        yield net_transmit_errors
        yield net_transmit_drops
        yield blk_read_request
        yield blk_read_bytes
        yield blk_read_seconds
        yield blk_write_request
        yield blk_write_seconds
        yield blk_write_bytes
        yield blk_flush_requests
        yield blk_flush_seconds
