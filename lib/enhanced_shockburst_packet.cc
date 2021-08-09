/* -*- c++ -*- */
/*
 * Copyright 2016 Bastille Networks
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */


#include <string.h>
#include <stdio.h>
#include <arpa/inet.h>

#include "enhanced_shockburst_packet.h"

enhanced_shockburst_packet::enhanced_shockburst_packet(uint8_t address_length,
                                                       uint8_t big_packet,
                                                       uint8_t payload_length,
                                                       uint8_t sequence_number,
                                                       uint8_t no_ack,
                                                       uint8_t crc_length,
                                                       uint8_t * address,
                                                       uint8_t * payload
                                                       ) :
  m_address_length(address_length),
  m_big_packet(big_packet),
  m_payload_length(payload_length),
  m_sequence_number(sequence_number),
  m_no_ack(no_ack),
  m_crc_length(crc_length)
{
  // Allocate buffers
  m_address = new uint8_t[m_address_length];
  m_payload = new uint8_t[m_payload_length];
  m_crc = new uint8_t[m_crc_length];

  // Copy over address and payload
  memcpy(m_address, address, m_address_length);
  memcpy(m_payload, payload, m_payload_length);

  // Build the packet bytes
  const int blen = 3 /* preamble + PCF */ +
                   m_crc_length +
                   m_address_length +
                   m_payload_length;
  m_packet_length_bytes = blen;
  m_packet_length_bits = blen*8;
  m_packet_bytes = new uint8_t[blen];

  memset(m_packet_bytes, 0, blen);

  // Preamble
  if((address[0] & 0x80) == 0x80) m_packet_bytes[0] = 0xAA;
  else m_packet_bytes[0] = 0x55;

  // Address
  memcpy(&m_packet_bytes[1], address, m_address_length);

  uint8_t alignment_offset;
  // PCF
  if (!big_packet)
  {
      m_packet_bytes[1 + m_address_length] = (m_payload_length & 0x3F) << 2;
      m_packet_bytes[1 + m_address_length] |= (m_sequence_number & 0x3);
      m_packet_bytes[2 + m_address_length] = m_no_ack << 7;
      alignment_offset = 1;
  }
  else { // 8-bits for payload length when NRF_ESB_MAX_PAYLOAD_LENGTH > 32
      m_packet_bytes[1 + m_address_length] = m_payload_length;
      m_packet_bytes[2 + m_address_length] = (m_sequence_number & 0x3) << 6;
      m_packet_bytes[2 + m_address_length] |= m_no_ack << 5;
      alignment_offset = 3;
  }

  // Payload
  for(int b = 0; b < m_payload_length; b++)
  {
    m_packet_bytes[2 + m_address_length + b] |= (payload[b] >> alignment_offset);
    m_packet_bytes[3 + m_address_length + b] |= (payload[b] << (8 - alignment_offset));
  }

  // Calculate the CRC
  uint16_t crc = 0xFFFF;
  for(int b = 1; b < 7 + m_payload_length; b++)
      crc = crc_update(crc, m_packet_bytes[b]);

  crc = crc_update(crc, m_packet_bytes[7 + m_payload_length] & (0xFF << (8 - alignment_offset)), alignment_offset);

  memcpy(m_crc, &crc, m_crc_length);

  m_packet_bytes[2 + m_address_length + m_payload_length] |= ((crc >> (8 + alignment_offset)) & 0xFF);
  m_packet_bytes[3 + m_address_length + m_payload_length] |= ((crc >> alignment_offset) & 0xFF);
  m_packet_bytes[4 + m_address_length + m_payload_length] |= ((crc << (8 - alignment_offset)) & (0xFF << (8 - alignment_offset)));
}

// Destructur
enhanced_shockburst_packet::~enhanced_shockburst_packet()
{
  delete[] m_address;
  delete[] m_payload;
  delete[] m_crc;
}

// Attempt to parse a packet from some incoming bytes using small packet protocol first, then large packet protocol
bool enhanced_shockburst_packet::try_parse(const uint8_t * bytes,
                                           const uint8_t ** addresses,
                                           const uint8_t *address_match_len,
                                           uint8_t address_length,
                                           uint8_t crc_length,
                                           enhanced_shockburst_packet *& packet)
{
    if (!enhanced_shockburst_packet::_try_parse(bytes,
                                                     addresses,
                                                     address_match_len,
                                                     address_length,
                                                     crc_length,
                                                     packet,
                                                     false))
    {
        return enhanced_shockburst_packet::_try_parse(bytes,
                                                         addresses,
                                                         address_match_len,
                                                         address_length,
                                                         crc_length,
                                                         packet,
                                                         true);
    }

    return true;
}
bool enhanced_shockburst_packet::_try_parse(const uint8_t * bytes,
    const uint8_t ** addresses,
    const uint8_t * address_match_len,
    uint8_t address_length,
    uint8_t crc_length,
    enhanced_shockburst_packet * &packet,
    bool big_packet)
{
  // Read the payload length
  uint8_t payload_length;
  uint8_t alignment_offset;
  
  if (big_packet) {
      payload_length = bytes[6];
      alignment_offset = 3;

      if (payload_length > 252)
          return false;
  }
  else {
      payload_length = bytes[6] >> 2;
      alignment_offset = 1;

      if (payload_length > 32)
          return false;
  }

  // Read the address
  uint8_t * address = new uint8_t[address_length];
  memcpy(address, &bytes[1], address_length);

  // Read the given CRC
  uint16_t crc_given;
  crc_given = bytes[2 + address_length + payload_length] & (0xFF >> alignment_offset);
  crc_given <<= 8;
  crc_given |= bytes[3 + address_length + payload_length];
  crc_given <<= alignment_offset;
  crc_given |= bytes[4 + address_length + payload_length] >> (8 - alignment_offset) ;
  crc_given = htons(crc_given);


  // Calculate the CRC
  uint16_t crc = 0xFFFF;
  for(int b = 1; b < 7 + payload_length; b++) crc = crc_update(crc, bytes[b]);
  crc = crc_update(crc, bytes[7 + payload_length] & (0xFF << (8 - alignment_offset)), alignment_offset);
  crc = htons(crc);

  // Validate the CRC
  if(memcmp(&crc, &crc_given, 2) != 0)
  {
      // If we've been provided a list of possible addresses, look for those so we can report CRC errors
      // Only check this if we're in the big_packet round of parsing, otherwise will report valid BP
      // packets during the non-BP parsing round.
      if (address_match_len && big_packet)
      {
          const uint8_t* cur_match_len = address_match_len;
          const uint8_t** cur_addr_match = addresses;
	  
          while (*cur_match_len)
          {
              if (memcmp(address, *cur_addr_match, *cur_match_len) == 0)
              {
                  printf("Possible NRF packet with CRC error (given: %04X, calculated: %04X, length: %d, address: ",
                        crc_given, crc, payload_length);
                  for (int i = 0; i < address_length; i++) printf("%02X",address[i]);
                  printf(")\n");
                  break;
              }
              cur_match_len++;
              cur_addr_match++;
          }
      }
      
      delete[] address;
      return false;
  }

  // Read the sequence number and no-ACK bit
  uint8_t seq;
  uint8_t no_ack;

  if (big_packet)
  {
      seq = bytes[7] >> 6;
      no_ack = (bytes[7] >> 5) & 0x01;
  } 
  else {
      seq = bytes[6] & 0x3;
      no_ack = bytes[7] >> 7;
  }  

  // Read the payload
  uint8_t payload[252];

  // Payload
  for (int b = 0; b < payload_length; b++)
  {
      payload[b] = bytes[7 + b] << alignment_offset;
      payload[b] |= bytes[8 + b] >> (8 - alignment_offset);
  }

  // Update the fields
  packet = new enhanced_shockburst_packet(address_length, 
                                          big_packet,
                                          payload_length, 
                                          seq,
                                          no_ack,
                                          crc_length,
                                          address,
                                          payload);
  
  // Cleanup
  delete[] address;

  return true;
}

// Print the packet details to standard out
void enhanced_shockburst_packet::print()
{
  printf("Address: ");
  for(int x = 0; x < m_address_length; x++) printf("%02X ", m_address[x]);
  printf("\n");

  printf("Payload: ");
  for(int x = 0; x < m_payload_length; x++) printf("%02X ", m_payload[x]);
  printf("\n");

  printf("CRC:     ");
  for(int x = 0; x < m_crc_length; x++) printf("%02X ", m_crc[x]);
  printf("\n");

  printf("Bytes:   ");
  for(int x = 0; x < m_packet_length_bytes; x++) printf("%02X ", m_packet_bytes[x]);
  printf("BP:      %d\n", m_big_packet);
  printf("ACK:     %d\n", m_no_ack);
  
  printf("\n"); 

  printf("\n");
}

// Process a crc byte (or partial byte)
uint16_t enhanced_shockburst_packet::crc_update (uint16_t crc, uint8_t data, uint8_t bits)
{
  crc = crc ^ ((uint16_t)data << 8);
  for (int x = 0; x < bits; x++)
  {
    if(crc & 0x8000) crc = (crc << 1) ^ 0x1021;
    else crc <<= 1;
  }
  return crc;
}
