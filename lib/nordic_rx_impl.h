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

#ifndef INCLUDED_NORDIC_NORDIC_RX_IMPL_H
#define INCLUDED_NORDIC_NORDIC_RX_IMPL_H

#include <nordic/nordic_rx.h>
#include <boost/crc.hpp>
#include "bit_shifting_byte_vector.h"
#include "enhanced_shockburst_packet.h"

namespace gr {
  namespace nordic {

    class nordic_rx_impl : public nordic_rx
    {
     private:

      // CRC16-CCITT
      boost::crc_optimal<16, 0x1021, 0, 0, false, false> m_crc;

      // Configuration 
      uint8_t m_address_length;
      uint8_t m_crc_length;
      uint8_t m_channel; 
      uint8_t m_data_rate;
      uint8_t** m_addresses;
      uint8_t* m_address_match_len;

      // Incoming bit/byte vector
      bit_shifting_byte_vector m_decoded_bits_bytes;

      // Enhanced shockburst packet
      enhanced_shockburst_packet * m_enhanced_shockburst;

     public:

      // Constructor/destructor
      nordic_rx_impl(const uint8_t channel,
                     const uint8_t address_length,
                     const uint8_t crc_length,
                     const uint8_t data_rate,
		     const std::string &address_match);
      ~nordic_rx_impl();

      // Main work method
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);

      // Channel getter/setter
      uint8_t get_channel();
      void set_channel(uint8_t channel);
    };

  } // namespace nordic
} // namespace gr

#endif /* INCLUDED_NORDIC_NORDIC_RX_IMPL_H */

