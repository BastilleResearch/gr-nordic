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


#ifndef INCLUDED_NORDIC_NORDIC_RX_H
#define INCLUDED_NORDIC_NORDIC_RX_H

#include <nordic/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace nordic {

    /*!
     * \brief <+description of block+>
     * \ingroup nordic
     *
     */
    class NORDIC_API nordic_rx : virtual public gr::sync_block
    {
     public:
      typedef std::shared_ptr<nordic_rx> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of nordic::nordic_rx.
       *
       * To avoid accidental use of raw pointers, nordic::nordic_rx's
       * constructor is in a private implementation
       * class. nordic::nordic_rx::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint8_t channel=0,
                       uint8_t address_length=5,
                       uint8_t crc_length=2,
                       uint8_t data_rate=0);

      // Channel getter/setter
      virtual uint8_t get_channel()=0;
      virtual void set_channel(uint8_t channel)=0;
    };

  } // namespace nordic
} // namespace gr

#endif /* INCLUDED_NORDIC_NORDIC_RX_H */

