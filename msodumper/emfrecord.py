#!/usr/bin/env python2
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from docdirstream import DOCDirStream
import wmfrecord

# The FormatSignature enumeration defines valuesembedded data in EMF records.
FormatSignature = {
    0x464D4520: "ENHMETA_SIGNATURE",
    0x46535045: "EPS_SIGNATURE"
}


class EMFStream(DOCDirStream):
    def __init__(self, bytes):
        DOCDirStream.__init__(self, bytes)

    def dump(self):
        print '<stream type="EMF" size="%d">' % self.size
        emrHeader = EmrHeader(self)
        emrHeader.dump()
        for i in range(emrHeader.header.Records):
            id = self.getuInt32()
            record = RecordType[id]
            type = record[0]
            size = self.getuInt32(pos=self.pos + 4)
            # EmrHeader is already dumped
            if i:
                print '<record index="%s" type="%s">' % (i, type)
                if len(record) > 1:
                    handler = record[1](self)
                    handler.dump()
                else:
                    print '<todo/>'
                print '</record>'
            self.pos += size
        print '</stream>'


class EMFRecord(DOCDirStream):
    def __init__(self, parent):
        DOCDirStream.__init__(self, parent.bytes)
        self.parent = parent
        self.pos = parent.pos


class EmrSavedc(EMFRecord):
    """This record saves the current state of the playback device context."""
    def __init__(self, parent):
        EMFRecord.__init__(self, parent)

    def dump(self):
        posOrig = self.pos
        self.printAndSet("Type", self.readuInt32())
        self.printAndSet("Size", self.readuInt32(), hexdump=False)
        assert self.pos - posOrig == self.Size


class EmrHeader(EMFRecord):
    """The EMR_HEADER record types define the starting points of EMF metafiles."""
    def __init__(self, parent):
        EMFRecord.__init__(self, parent)

    def dump(self):
        print '<emrHeader>'
        self.printAndSet("Type", self.readuInt32())
        self.printAndSet("Size", self.readuInt32(), hexdump=False)
        self.header = Header(self)
        self.header.dump()
        if self.Size >= 100:
            HeaderExtension1(self).dump()
        if self.Size >= 108:
            HeaderExtension2(self).dump()
        print '</emrHeader>'


class Header(EMFRecord):
    """The Header object defines the EMF metafile header."""
    def __init__(self, parent):
        EMFRecord.__init__(self, parent)

    def dump(self):
        posOrig = self.pos
        print("<header>")
        wmfrecord.RectL(self, "Bounds").dump()
        wmfrecord.RectL(self, "Frame").dump()
        self.printAndSet("RecordSignature", self.readuInt32(), dict=FormatSignature)
        self.printAndSet("Version", self.readuInt32())
        self.printAndSet("Bytes", self.readuInt32(), hexdump=False)
        self.printAndSet("Records", self.readuInt32(), hexdump=False)
        self.printAndSet("Handles", self.readuInt16(), hexdump=False)
        self.printAndSet("Reserved", self.readuInt16(), hexdump=False)
        self.printAndSet("nDescription", self.readuInt32(), hexdump=False)
        self.printAndSet("offDescription", self.readuInt32(), hexdump=False)
        self.printAndSet("nPalEntries", self.readuInt32(), hexdump=False)
        wmfrecord.SizeL(self, "Device").dump()
        wmfrecord.SizeL(self, "Millimeters").dump()
        print("</header>")
        assert posOrig == self.pos - 80
        self.parent.pos = self.pos


class HeaderExtension1(EMFRecord):
    """The HeaderExtension1 object defines the first extension to the EMF metafile header."""
    def __init__(self, parent):
        EMFRecord.__init__(self, parent)

    def dump(self):
        posOrig = self.pos
        print("<headerExtension1>")
        self.printAndSet("cbPixelFormat", self.readuInt32(), hexdump=False)
        self.printAndSet("offPixelFormat", self.readuInt32(), hexdump=False)
        self.printAndSet("bOpenGL", self.readuInt32())
        print("</headerExtension1>")
        assert posOrig == self.pos - 12
        self.parent.pos = self.pos


class HeaderExtension2(EMFRecord):
    """The HeaderExtension1 object defines the first extension to the EMF metafile header."""
    def __init__(self, parent):
        EMFRecord.__init__(self, parent)

    def dump(self):
        posOrig = self.pos
        print("<headerExtension2>")
        self.printAndSet("MicrometersX", self.readuInt32(), hexdump=False)
        self.printAndSet("MicrometersY", self.readuInt32(), hexdump=False)
        print("</headerExtension2>")
        assert posOrig == self.pos - 8
        self.parent.pos = self.pos

"""The RecordType enumeration defines values that uniquely identify EMF records."""
RecordType = {
    0x00000001: ['EMR_HEADER'],
    0x00000002: ['EMR_POLYBEZIER'],
    0x00000003: ['EMR_POLYGON'],
    0x00000004: ['EMR_POLYLINE'],
    0x00000005: ['EMR_POLYBEZIERTO'],
    0x00000006: ['EMR_POLYLINETO'],
    0x00000007: ['EMR_POLYPOLYLINE'],
    0x00000008: ['EMR_POLYPOLYGON'],
    0x00000009: ['EMR_SETWINDOWEXTEX'],
    0x0000000A: ['EMR_SETWINDOWORGEX'],
    0x0000000B: ['EMR_SETVIEWPORTEXTEX'],
    0x0000000C: ['EMR_SETVIEWPORTORGEX'],
    0x0000000D: ['EMR_SETBRUSHORGEX'],
    0x0000000E: ['EMR_EOF'],
    0x0000000F: ['EMR_SETPIXELV'],
    0x00000010: ['EMR_SETMAPPERFLAGS'],
    0x00000011: ['EMR_SETMAPMODE'],
    0x00000012: ['EMR_SETBKMODE'],
    0x00000013: ['EMR_SETPOLYFILLMODE'],
    0x00000014: ['EMR_SETROP2'],
    0x00000015: ['EMR_SETSTRETCHBLTMODE'],
    0x00000016: ['EMR_SETTEXTALIGN'],
    0x00000017: ['EMR_SETCOLORADJUSTMENT'],
    0x00000018: ['EMR_SETTEXTCOLOR'],
    0x00000019: ['EMR_SETBKCOLOR'],
    0x0000001A: ['EMR_OFFSETCLIPRGN'],
    0x0000001B: ['EMR_MOVETOEX'],
    0x0000001C: ['EMR_SETMETARGN'],
    0x0000001D: ['EMR_EXCLUDECLIPRECT'],
    0x0000001E: ['EMR_INTERSECTCLIPRECT'],
    0x0000001F: ['EMR_SCALEVIEWPORTEXTEX'],
    0x00000020: ['EMR_SCALEWINDOWEXTEX'],
    0x00000021: ['EMR_SAVEDC', EmrSavedc],
    0x00000022: ['EMR_RESTOREDC'],
    0x00000023: ['EMR_SETWORLDTRANSFORM'],
    0x00000024: ['EMR_MODIFYWORLDTRANSFORM'],
    0x00000025: ['EMR_SELECTOBJECT'],
    0x00000026: ['EMR_CREATEPEN'],
    0x00000027: ['EMR_CREATEBRUSHINDIRECT'],
    0x00000028: ['EMR_DELETEOBJECT'],
    0x00000029: ['EMR_ANGLEARC'],
    0x0000002A: ['EMR_ELLIPSE'],
    0x0000002B: ['EMR_RECTANGLE'],
    0x0000002C: ['EMR_ROUNDRECT'],
    0x0000002D: ['EMR_ARC'],
    0x0000002E: ['EMR_CHORD'],
    0x0000002F: ['EMR_PIE'],
    0x00000030: ['EMR_SELECTPALETTE'],
    0x00000031: ['EMR_CREATEPALETTE'],
    0x00000032: ['EMR_SETPALETTEENTRIES'],
    0x00000033: ['EMR_RESIZEPALETTE'],
    0x00000034: ['EMR_REALIZEPALETTE'],
    0x00000035: ['EMR_EXTFLOODFILL'],
    0x00000036: ['EMR_LINETO'],
    0x00000037: ['EMR_ARCTO'],
    0x00000038: ['EMR_POLYDRAW'],
    0x00000039: ['EMR_SETARCDIRECTION'],
    0x0000003A: ['EMR_SETMITERLIMIT'],
    0x0000003B: ['EMR_BEGINPATH'],
    0x0000003C: ['EMR_ENDPATH'],
    0x0000003D: ['EMR_CLOSEFIGURE'],
    0x0000003E: ['EMR_FILLPATH'],
    0x0000003F: ['EMR_STROKEANDFILLPATH'],
    0x00000040: ['EMR_STROKEPATH'],
    0x00000041: ['EMR_FLATTENPATH'],
    0x00000042: ['EMR_WIDENPATH'],
    0x00000043: ['EMR_SELECTCLIPPATH'],
    0x00000044: ['EMR_ABORTPATH'],
    0x00000046: ['EMR_COMMENT'],
    0x00000047: ['EMR_FILLRGN'],
    0x00000048: ['EMR_FRAMERGN'],
    0x00000049: ['EMR_INVERTRGN'],
    0x0000004A: ['EMR_PAINTRGN'],
    0x0000004B: ['EMR_EXTSELECTCLIPRGN'],
    0x0000004C: ['EMR_BITBLT'],
    0x0000004D: ['EMR_STRETCHBLT'],
    0x0000004E: ['EMR_MASKBLT'],
    0x0000004F: ['EMR_PLGBLT'],
    0x00000050: ['EMR_SETDIBITSTODEVICE'],
    0x00000051: ['EMR_STRETCHDIBITS'],
    0x00000052: ['EMR_EXTCREATEFONTINDIRECTW'],
    0x00000053: ['EMR_EXTTEXTOUTA'],
    0x00000054: ['EMR_EXTTEXTOUTW'],
    0x00000055: ['EMR_POLYBEZIER16'],
    0x00000056: ['EMR_POLYGON16'],
    0x00000057: ['EMR_POLYLINE16'],
    0x00000058: ['EMR_POLYBEZIERTO16'],
    0x00000059: ['EMR_POLYLINETO16'],
    0x0000005A: ['EMR_POLYPOLYLINE16'],
    0x0000005B: ['EMR_POLYPOLYGON16'],
    0x0000005C: ['EMR_POLYDRAW16'],
    0x0000005D: ['EMR_CREATEMONOBRUSH'],
    0x0000005E: ['EMR_CREATEDIBPATTERNBRUSHPT'],
    0x0000005F: ['EMR_EXTCREATEPEN'],
    0x00000060: ['EMR_POLYTEXTOUTA'],
    0x00000061: ['EMR_POLYTEXTOUTW'],
    0x00000062: ['EMR_SETICMMODE'],
    0x00000063: ['EMR_CREATECOLORSPACE'],
    0x00000064: ['EMR_SETCOLORSPACE'],
    0x00000065: ['EMR_DELETECOLORSPACE'],
    0x00000066: ['EMR_GLSRECORD'],
    0x00000067: ['EMR_GLSBOUNDEDRECORD'],
    0x00000068: ['EMR_PIXELFORMAT'],
    0x00000069: ['EMR_DRAWESCAPE'],
    0x0000006A: ['EMR_EXTESCAPE'],
    0x0000006C: ['EMR_SMALLTEXTOUT'],
    0x0000006D: ['EMR_FORCEUFIMAPPING'],
    0x0000006E: ['EMR_NAMEDESCAPE'],
    0x0000006F: ['EMR_COLORCORRECTPALETTE'],
    0x00000070: ['EMR_SETICMPROFILEA'],
    0x00000071: ['EMR_SETICMPROFILEW'],
    0x00000072: ['EMR_ALPHABLEND'],
    0x00000073: ['EMR_SETLAYOUT'],
    0x00000074: ['EMR_TRANSPARENTBLT'],
    0x00000076: ['EMR_GRADIENTFILL'],
    0x00000077: ['EMR_SETLINKEDUFIS'],
    0x00000078: ['EMR_SETTEXTJUSTIFICATION'],
    0x00000079: ['EMR_COLORMATCHTOTARGETW'],
    0x0000007A: ['EMR_CREATECOLORSPACEW']
}

# vim:set filetype=python shiftwidth=4 softtabstop=4 expandtab: