/* -*- c++ -*- */

#define NORDIC_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "nordic_swig_doc.i"

%{
#include "nordic/nordic_rx.h"
#include "nordic/nordic_tx.h"
%}


%include "nordic/nordic_rx.h"
GR_SWIG_BLOCK_MAGIC2(nordic, nordic_rx);
%include "nordic/nordic_tx.h"
GR_SWIG_BLOCK_MAGIC2(nordic, nordic_tx);
