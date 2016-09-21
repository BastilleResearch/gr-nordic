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

#ifndef INCLUDED_NORDIC_NORDIC_TX_IMPL_H
#define INCLUDED_NORDIC_NORDIC_TX_IMPL_H

#include <nordic/nordic_tx.h>
#include <queue>

namespace gr {
  namespace nordic {

    class nordic_tx_impl : public nordic_tx
    {
     private:

      // TX nordictap queue
      std::queue<pmt::pmt_t> m_tx_queue;

      // Lookup table to unpack bytes to bits (NRZ)
      char m_unpack_table[256][8];

      // Number of output channels
      uint8_t m_channel_count;

      // Incoming message handler
      void nordictap_message_handler(pmt::pmt_t msg);

      // Process a crc byte (or partial byte)
      uint16_t crc_update (uint16_t crc, uint8_t data, uint8_t bits=8);

     public:
      nordic_tx_impl(uint8_t channel_count);
      ~nordic_tx_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace nordic
} // namespace gr

#endif /* INCLUDED_NORDIC_NORDIC_TX_IMPL_H */

