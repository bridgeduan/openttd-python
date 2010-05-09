#!/usr/bin/env python
# reading OpenTTD / TTDPatch GRF files with python
# made by yorickvanpelt {AT} gmail {DOT} com
import optparse
import openttd.newgrf
import sys
import Image # PIL
def saverealsprite(sprite, name, palette):
    im = Image.fromstring('P', (sprite.width, sprite.height), sprite.data)
    im.putpalette(palette.data)
    im.save(name)
def decode(file, palette):
    print "Reading file..."
    c = openttd.newgrf.NewGRFParser(file=file)
    c.readfile()
    spr = 0
    print "Reading sprite...",
    if sys.stdout.isatty():
        while c.rdp.offset != c.rdp.size-4:
            if c.readsprite(): spr += 1
            if (spr % 100) == 0:
                print "%4d" % spr, "\x1B[6D",
                sys.stdout.flush()
    else:
        while c.rdp.offset != c.rdp.size-4:
            if c.readsprite(): spr += 1
    print "\nTotal %d sprites" % len(c.sprites)
    return c
def save(palette, c, outfile):
    print "Saving nfo..."
    spr = 0
    for sprite in c.sprites:
        if type(sprite) is openttd.newgrf.NewGRFFirstSprite or type(sprite) is openttd.newgrf.NewGRFAction:
            print >>outfile,"%d * %d" % (spr, sprite.size),' '.join('%02X' % ord(c) for c in sprite.data)
        elif type(sprite) is openttd.newgrf.NewGRFRealSprite:
            print >>outfile,"%d sprite%d.png %02X %d %d" % (spr, spr, sprite.type, sprite.x_offs, sprite.y_offs)
            saverealsprite(sprite, "sprite%d.png" % spr, palette)
        spr += 1
def main():
    argparser = optparse.OptionParser()
    argparser.set_defaults(use_psyco=0, palette="pals/ttw_norm.bcp")
    argparser.add_option("-d", "--decode", dest="decodefilename", help="decode FILE", metavar="FILE")
    argparser.add_option("-p", "--palette", dest="palette", help="palette file to use")
    argparser.add_option("-o", "--outfile", dest="outfile", help="where to store nfo/grf")
    argparser.add_option("--enable-psyco", dest="use_psyco", action="store_const", const=1, help="Force using psyco")
    argparser.add_option("--disable-psyco", dest="use_psyco", action="store_const", const=-1, help="Don't use psyco")
    try:
        (options, args) = argparser.parse_args()
    except optparse.OptionError, err:
        print "Error while parsing arguments: ", err
        argparser.print_help()
        return
    except TypeError, err:
        print "Error while parsing arguments: ", err
        argparser.print_help()
        return
    if options.use_psyco > -1:
        # Import Psyco if available
        try:
            import psyco
            psyco.full()
            print "using psyco..."
        except ImportError:
            if options.use_psyco > 0:
                print "Error: could not import psyco"
                sys.exit(1)
    if options.decodefilename:
        try:
            file = open(options.decodefilename, 'rb')
            palette = openttd.newgrf.NewGRFPalette()
            palette.loadfrombcpfile(options.palette)
        except IOError, e:
            print "Error while reading file:", e
            return
            #raise
        c = decode(file, palette)
        file.close()
        if options.outfile:
            outfile = open(options.outfile, "w")
        else:
            outfile = open(options.decodefilename+".nfo", "w")
        save(palette, c, outfile)
        outfile.close()
    else:
        argparser.print_help()
    
if __name__ == '__main__':
    main()