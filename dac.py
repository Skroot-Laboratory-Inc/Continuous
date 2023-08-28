import hid

import logger


class Dac:
    def __init__(self):
        self.disabled = False
        PRODUCT_ID = 71  # Set the product id to match your ADU device. See list here: https://www.ontrak.net/Nodll.htm
        VENDOR_ID = 0x0a07
        try:
            self.device = hid.device()
            self.device.open(VENDOR_ID, PRODUCT_ID)
        except:
            self.disabled = True
            logger.exception("Failed to initialize DAC")

    def send_ma(self, mA):
        if not self.disabled:
            bits = mA_to_bits(mA)
            write_to_adu(self.device, f'wr{bits}')
        else:
            pass


def write_to_adu(dev, msg_str):
    logger.info('Writing command: {}'.format(msg_str))
    # message structure:
    #   message is an ASCII string containing the command
    #   8 bytes in length
    #   0th byte must always be 0x01 (decimal 1)
    #   bytes 1 to 7 are ASCII character values representing the command
    #   remainder of message is padded to 8 bytes with character code 0
    byte_str = chr(0x01) + msg_str + chr(0) * max(7 - len(msg_str), 0)
    try:
        num_bytes_written = dev.write(byte_str.encode())
    except IOError as e:
        logger.exception('Error writing command: {}'.format(e))
        return None
    return num_bytes_written


def mA_to_bits(mA):
    bits = mA * 3276.75
    return int(round(bits, 0))
