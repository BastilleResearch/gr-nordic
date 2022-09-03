/* -*- c++ -*- */
/*
 * Copyright 2016 Bastille Networks.
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <pmt/pmt.h>
#include <boost/asio.hpp>
#include <boost/algorithm/hex.hpp>
#include "nordic_rx_impl.h"
#include "nordictap.h"

namespace gr {
  namespace nordic {

    nordic_rx::sptr
    nordic_rx::make(const uint8_t channel,
                    const uint8_t address_length,
                    const uint8_t crc_length,
                    const uint8_t data_rate,
                    const std::string &address_match)
    {
      return gnuradio::get_initial_sptr
        (new nordic_rx_impl(channel, address_length, crc_length, data_rate, address_match));
    }

    /*
     * The private constructor
     */
    nordic_rx_impl::nordic_rx_impl(const uint8_t channel,
                                   const uint8_t address_length,
                                   const uint8_t crc_length,
                                   const uint8_t data_rate,
                                   const std::string &address_match)
      : gr::sync_block("nordic_rx",
              gr::io_signature::make(1, 1, sizeof(uint8_t)),
              gr::io_signature::make(0, 0, 0)),
              m_decoded_bits_bytes(262*8 /* buffer sufficient for max ESB frame length */), // ESB payload can be up to 252 bytes plus header+crc
              m_crc_length(crc_length),
              m_address_length(address_length),
              m_channel(channel),
              m_data_rate(data_rate),
              m_addresses(NULL),
              m_address_match_len(NULL)
    {
        // Parse list of addresses
        if (!address_match.empty())
        {
 	    std::string match_buffer = address_match;
            int n_addresses = std::count(match_buffer.begin(), match_buffer.end(), ',') + 1;

	    m_addresses = new uint8_t *[n_addresses];
	    for (int i = 0; i < n_addresses; i++)
	      m_addresses[i] = new uint8_t[address_length];
	    
            m_address_match_len = new uint8_t[n_addresses + 1];
            m_address_match_len[n_addresses] = 0;

            int cur_address = 0;
            size_t e = 0;

	    std::string::iterator s = match_buffer.begin();
            do 
            {
  	        e = match_buffer.find(',', s - match_buffer.begin());

		if (e == std::string::npos)
		  e = match_buffer.end() - match_buffer.begin();
		
                m_address_match_len[cur_address] = std::min((e - (s - match_buffer.begin())) / 2, (size_t) address_length);

                try {
		  std::string hex_address = boost::algorithm::unhex(match_buffer.substr(s - match_buffer.begin(), m_address_match_len[cur_address] * 2));
                    memcpy(m_addresses[cur_address], hex_address.c_str(), m_address_match_len[cur_address]);
                    cur_address++;
                }
                catch (boost::algorithm::hex_decode_error hde) {
                    printf("Warning, invalid hex data provided as address match list to nordic_rx\n");
                }

                s += (e - (s - match_buffer.begin())) + 1;
	    } while (s < match_buffer.end());
        }

      message_port_register_out(pmt::mp("nordictap_out"));
    }

    /*
     * Our virtual destructor.
     */
    nordic_rx_impl::~nordic_rx_impl()
    {
        if (m_addresses)
	  {
	    for (int i = 0; i < 1; i++)
	      delete[] m_addresses[i];
	    delete[] m_addresses;
	  }

        if (m_address_match_len)
            delete[] m_address_match_len;
    }

    int
    nordic_rx_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const uint8_t *in = (const uint8_t *) input_items[0];

      // Step through the incoming demodulated bits
      for(int x = 0; x < noutput_items; x++)
      {
        // Add the incoming bit to the bit shifted byte array
        m_decoded_bits_bytes.add_bit(in[x]);
        const uint8_t * bytes = m_decoded_bits_bytes.bytes();

        // Check for a valid preamble
        if(bytes[0] == 0xAA || bytes[0] == 0x55)
        {
          // Check for a valid first address bit
          if((bytes[0] & 0x80) == (bytes[1] & 0x80))
          {	      
            // Attempt to decode a payload
            if(enhanced_shockburst_packet::try_parse(bytes,
                                                     (const uint8_t **) m_addresses,
                                                     (const uint8_t *) m_address_match_len,
                                                     m_address_length,
                                                     m_crc_length,
                                                     m_enhanced_shockburst))
            {
              // m_enhanced_shockburst->print();
              
              // Build the wireshark header
              nordictap_header header;
              header.channel = m_channel;
              header.data_rate = m_data_rate;
              header.address_length = m_address_length;
              header.big_packet = m_enhanced_shockburst->big_packet();
              header.payload_length = m_enhanced_shockburst->payload_length();
              header.sequence_number = m_enhanced_shockburst->sequence_number();
              header.no_ack = m_enhanced_shockburst->no_ack();
              header.crc_length = m_crc_length;

              // Concatenate the header, address, payload, and CRC
              uint8_t buffer_length = sizeof(nordictap_header) + m_address_length + header.payload_length + m_crc_length;
              uint8_t * buffer = new uint8_t[buffer_length];
              memcpy(&buffer[0], &header, sizeof(nordictap_header));
              memcpy(&buffer[sizeof(nordictap_header)], m_enhanced_shockburst->address(), m_address_length);
              memcpy(&buffer[sizeof(nordictap_header) + m_address_length], m_enhanced_shockburst->payload(), header.payload_length);
              memcpy(&buffer[sizeof(nordictap_header) + m_address_length + header.payload_length], m_enhanced_shockburst->crc(), m_crc_length);
              
              //printf("Buffer=%s", buffer);
              //printf("\n");

              // Send the packet to wireshark
              boost::asio::io_service io_service;
              boost::asio::ip::udp::resolver resolver(io_service);
              boost::asio::ip::udp::resolver::query query(boost::asio::ip::udp::v4(), "127.0.0.1", "9451");
              boost::asio::ip::udp::endpoint receiver_endpoint = *resolver.resolve(query);
              boost::asio::ip::udp::socket socket(io_service);
              socket.open(boost::asio::ip::udp::v4());
              socket.send_to(boost::asio::buffer(buffer, buffer_length), receiver_endpoint);

              // Send the packet to nordictap_out
              message_port_pub(pmt::intern("nordictap_out"), pmt::init_u8vector(buffer_length, buffer));

              // Cleanup
              delete[] buffer;
            }
          }
        }
      }

      return noutput_items;
    }

    // Channel getter
    uint8_t nordic_rx_impl::get_channel()
    {
      return m_channel;
    }

    // Channel setter
    void nordic_rx_impl::set_channel(uint8_t channel)
    {
      m_channel = channel;
    }

  } /* namespace nordic */
} /* namespace gr */

