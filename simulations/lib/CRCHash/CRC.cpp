#include "CRC.h"
 
crc32::crc32() {
 
}
 
crc32::~crc32(){
}
 
const unsigned int crc32::getCrc32(unsigned int crc, const void *buf, int size){
   const unsigned char *p;
   p = (unsigned char *)buf;
   crc = crc ^ ~0U;
   while (size--){
      crc = crc32_tab[(crc ^ *p++) & 0xFF] ^ (crc >> 8);
   }
   return crc ^ ~0U;
}