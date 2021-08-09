#ifndef NORDICTAP_H
#define NORDICTAP_H

#define NORDICTAP_GSM_PORT 9451

// Data rates
#define NORDICTAP_RATE_250K 0
#define NORDICTAP_RATE_1M   1
#define NORDICTAP_RATE_2M   2

struct nordictap_header
{
  // Channel number
  uint8_t channel;

  // Data rate 
  uint8_t data_rate; 

  // Address length
  uint8_t address_length;

  // Payload length
  uint8_t payload_length;

  // Sequence number (ESB)
  uint8_t sequence_number;

  // No ACK bit (ESB)
  bool no_ack;

  // CRC length, in bytes
  uint8_t crc_length;

  // Big packet protocol
  bool big_packet;

} __attribute__((packed));

#endif // NORDICTAP_H