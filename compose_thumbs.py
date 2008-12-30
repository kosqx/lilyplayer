#!/usr/bin/env python

import Image
import ImageColor
import ImageDraw
import ImageFont

# optymalise
import StringIO



def compose(images, outfile, cols=2, size=150, border=10, header=None, ):
    rows = (len(images) + cols - 1) / cols

    result = None
    header_h = 0
    size_w, size_h = size, size
    
    font = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Verdana_Bold.ttf", 12, encoding="unic")

    for index, (data, label) in enumerate(images):
        print label
        x = index % cols
        y = index / cols
        
        file = StringIO.StringIO(data)
        im = Image.open(file)
        
        im.thumbnail((size_w, size_h), Image.ANTIALIAS)
        
        draw = ImageDraw.Draw(im)
        text = u'%s' % label
        textsize = draw.textsize(text, font=font)
        draw.text((im.size[0] - textsize[0] - 1, im.size[1] - textsize[1] - 1), text, fill=ImageColor.getrgb('#ff0000'), font=font)
        del draw 

        if result is None:
            if header is not None:
                max_w = 0
                header_h = border
                header_pos = []
                for name, value in header:
                    header_pos.append(header_h)
                    txtsize = font.getsize(name)
                    max_w = max(max_w, txtsize[0])
                    header_h += textsize[1] + 2
                   
            #print header_pos
            size_w, size_h = im.size
            result = Image.new(
                    'RGB',
                    (size_w * cols + (cols + 1) * border, header_h + size_h * rows + (rows + 1) * border),
                    ImageColor.getrgb('#eeeeee')
            )
            
            if header is not None:
                draw = ImageDraw.Draw(result)
                
                logo_text = "Lily Player"
                logo_font =  ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Verdana_Bold.ttf", 30, encoding="unic")
                logo_size = draw.textsize(logo_text, font=logo_font)
                print ((size_w + border) * cols - logo_size[0], border), logo_size, (size_w, border, cols, logo_size[0])
                draw.text(((size_w + border) * cols - logo_size[0], border), logo_text, fill=ImageColor.getrgb('#ffffff'), font=logo_font)
                                
                header_color = ImageColor.getrgb('#000000')
                for (name, value), header_y in zip(header, header_pos):
                    draw.text((border, header_y), name, fill=header_color, font=font)
                    draw.text((border + max_w + border + 5, header_y), value, fill=header_color, font=font)
                
                del draw

        
        
        result.paste(im, (x * size_w + (x + 1) * border, header_h + y * size_h + (y + 1) * border))
        
        file.close()
        
    result.save(outfile, 'PNG')

if False:

    images = [(file_read('img2/thumb_%.4d.png' % i), 'thumb_%.4d' % i) for i in xrange(1, 71)]
    
    make(images, size=200, cols=4, border=5,
            header=[('File Name', 'ala ma kota'), ('File Size', '123 MB'), ('Resolution', '42:37'), ('Duration', '42:37')]
    )
