# CalPack
Packets in Python Simplified without compromising speed.

This package is intended to make creating and/or parsing packets on the fly quick and easy.  This is a wrapper around the `cytpes` modules built-in to python.  

## Examples

### Creating a predefined packet:

    import calpack
    
    udp_pkt = calpack.ipv4.udp(
        source_ip = '192.168.0.1',
        dest_ip = '192.168.0.2',
        source_port = 8080,
        dest_port = 8080,
        data = range(100)
    )
    
### Creating Custom Packets
    
    from calpack import models
    
    
    class my_pkt(models.Packet):
        _word_size = 32
        _endian = models.ENDIAN_BIG
        
        # Word 0
        field0 = models.IntegerField()
        
        # Word 1
        field1 = models.IntegerField(bit_len=16)
        field2 = models.IntegerField(bit_len=4)
        field3 = models.IngegerField(bit_len=12)
        
        # Words 2 & 3
        field4 = models.IntegerField(bit_len=64)
        
        # Words 4-10
        field5 = models.IntegerField(num_words=7)        
        
### Encapsulating Custom Packets
        
    class my_small_pkt(models.Packet):
        _word_size = 16
        field1 = models.IntegerField()
        field2 = models.IntegerField()
        
    class my_big_pkt(models.Packet):
        _word_size = 32
        field1 = models.IntegerField()
        field2 = models.IntegerField()
        field3 = my_small_pkt
        
       
You can even mix 'endianess' of the encapsulated packet.
       
    class my_small_pkt(models.Packet):
        _word_size = 16
        _endian = models.ENDIAN_LITTLE
        field1 = models.IntegerField()
        field2 = models.uint16()
        
    class my_big_pkt(packet.Packet):
        _word_size = 32
        _endian = models.ENDIAN_BIG
        field1 = models.IntegerField()
        field2 = models.IntegerField()
        field3 = my_small_pkt
        