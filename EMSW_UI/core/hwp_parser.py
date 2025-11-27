import olefile
import zlib
from dataclasses import dataclass, classmethod

@dataclass
class Record:
    tagID: int =0
    level: int =0
    size: int =0

    def read_record(cls, tagID: int, bits: ) -> bool:
        """32비트 읽어 레코드 헤더 파싱"""
        record_bits = bits.read(32)
        cls.tagID, cls.level, cls.size = cls.split_header_bits(record_bits.bytes)

        if cls.tagID != tagID: # 읽어온 레코드가 예상과 다른 레코드일 경우
            return False

        # 3.
        if cls.size == 0xFFF:  # 4095, 확장 크기
            size_bytes = bits.read(32).bytes
            cls.size = bytes_to_int(size_bytes)

        return True