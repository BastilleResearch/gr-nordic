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


#ifndef BIT_SHIFTING_BYTE_VECTOR_H
#define BIT_SHIFTING_BYTE_VECTOR_H

// Byte vector that can be added to one bit at a time
class bit_shifting_byte_vector
{
public:

    // Constructor
    bit_shifting_byte_vector(int length);

    // Copy constructor
    bit_shifting_byte_vector(const bit_shifting_byte_vector &copy);

    // Destructor
    ~bit_shifting_byte_vector();

    // Add a new bit
    void add_bit(unsigned char bit);

    // Get the byte array
    const unsigned char * bytes() { return m_bytes; }

    // Get a previous byte array state
    const unsigned char * bytes(int index)
    {
        index += m_previous_state_read;
        while(index < 0) index += 7;
        while(index > 7) index -= 7;
        return m_previous_states[index];
    }

private:

    // Bytes - current state
    unsigned char * m_bytes;

    // Length, in bytes
    int m_length;

    // Bytes - previous 8 states
    unsigned char * m_previous_states[8];

    // Previous state index - write
    int m_previous_state_write;

    // Previous state index - read
    int m_previous_state_read;
};

#endif // BIT_SHIFTING_BYTE_VECTOR_H
