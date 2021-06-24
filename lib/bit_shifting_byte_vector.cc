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


#include "bit_shifting_byte_vector.h"

#include <cstring>

// Constructor
bit_shifting_byte_vector::bit_shifting_byte_vector(int length) :
    m_length(length),
    m_previous_state_write(7),
    m_previous_state_read(0)
{
    m_bytes = new unsigned char[m_length];
    for(int x = 0; x < 8; x++)
        m_previous_states[x] = new unsigned char[m_length];
}

// Copy constructor
bit_shifting_byte_vector::bit_shifting_byte_vector(const bit_shifting_byte_vector &copy)
{
    m_length = copy.m_length;
    m_bytes = new unsigned char[m_length];
    memcpy(m_bytes, copy.m_bytes, m_length);
    for(int x = 0; x < 8; x++)
    {
        m_previous_states[x] = new unsigned char[m_length];
        memcpy(m_previous_states[x], copy.m_previous_states[x], m_length);
    }
    m_previous_state_write = copy.m_previous_state_write;
    m_previous_state_read = copy.m_previous_state_read;
}

// Destructor
bit_shifting_byte_vector::~bit_shifting_byte_vector()
{
    delete[] m_bytes;
    for(int x = 0; x < 8; x++)
    {
        delete[] m_previous_states[x];
    }
}

// Add a new bit
void bit_shifting_byte_vector::add_bit(unsigned char bit)
{
    // Update the previous state vector
    memcpy(m_previous_states[m_previous_state_write], m_bytes, m_length);

    // For the left m_length-1 bytes, we'll
    // use values from m_previous_states
    memcpy(m_bytes, m_previous_states[m_previous_state_read]+1, m_length - 1);

    // For the rightmost byte, we'll tack on
    // the the current new bit
    m_bytes[m_length - 1] = m_bytes[m_length - 1] << 1 | bit;

    // Update the previous state indices
    if(++m_previous_state_read > 7) m_previous_state_read = 0;
    if(++m_previous_state_write > 7) m_previous_state_write = 0;
}