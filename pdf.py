from fpdf import FPDF

import logger


class PDF(FPDF):
    def setPageWidthHeight(self, height, width):
        self.pdf_w = width
        self.pdf_h = height

    def drawLine(self, xrel, yrel):
        self.set_line_width(0.0)
        self.line(0, self.pdf_h * yrel, self.pdf_w * xrel, self.pdf_h * yrel)

    def drawCircle(self, xrel, yrel, rrel, color):
        if color == 'green':
            self.set_fill_color(r=26, g=124, b=42)
        else:  # red
            self.set_fill_color(r=129, g=17, b=17)
        self.ellipse(x=self.pdf_w * xrel, y=self.pdf_h * yrel, w=self.pdf_h * rrel, h=self.pdf_h * rrel, style="FD")

    def placeImage(self, image, xrel, yrel, relwidth, relheight):
        self.set_xy(xrel, yrel)
        self.image(image, link='', type='', w=relwidth * self.pdf_w, h=relheight * self.pdf_h)

    def placePlot(self, plt, xrel, yrel, relwidth, relheight):
        self.set_xy(self.pdf_w * xrel, self.pdf_h * yrel)
        self.image(plt, link='', type='', w=relwidth * self.pdf_w, h=relheight * self.pdf_h)

    def placeText(self, text, xrel, yrel, relwidth, relheight, fontsize, bold):
        self.set_xy(self.pdf_w * xrel, self.pdf_h * yrel)
        if bold == True:
            self.set_font('Arial', 'B', fontsize)
            self.multi_cell(w=relwidth * self.pdf_w, h=relheight * self.pdf_h, align='C', txt=text, border=0)
        else:
            self.set_font('Arial', '', fontsize)
            self.multi_cell(w=relwidth * self.pdf_w, h=relheight * self.pdf_h, align='L', txt=text, border=0)

    def setAuthor(self):
        self.set_author('Skroot Laboratory')


def generatePdf(location, Readers):
    try:
        pdf = PDF(orientation='L', unit='mm',
                  format='A4')  # default = (orientation='P', unit='mm', format='A4')
        pdf.setPageWidthHeight(210, 297)
        labelWidth = 0.5
        plotWidth = 0.41
        paddingX = 0.02
        notesWidth = labelWidth - plotWidth

        totalHeight = 0.45
        labelHeight = 0.02
        paddingY = 0.05
        plotHeight = totalHeight - (paddingY + labelHeight)
        notesLineHeight = 0.02

        pdf.add_page()
        currentY = paddingX
        currentX = paddingX
        for Reader in Readers:
            try:
                oldX = currentX
                currentX, currentY = Reader.addToPdf(pdf, currentX, currentY, labelWidth, labelHeight,
                                                     plotWidth,
                                                     plotHeight, notesWidth, paddingY)
                currentX, currentY = Reader.addNotesToPdf(pdf, currentX, currentY, notesWidth, notesLineHeight,
                                                          plotHeight, paddingY)
                currentX, currentY = checkIfNewPage(pdf, currentX, currentY, labelHeight, plotHeight,
                                                    paddingX,
                                                    oldX, labelWidth)
            except:
                logger.exception(f'Failed to update pdf')
        pdf.placeText("Summary", currentX, currentY, labelWidth, labelHeight, 16, True)
        currentY += labelHeight
        pdf.placePlot(f'{location}/Summary Figure.jpg', currentX, currentY, plotWidth, plotHeight)
        pdf.setAuthor()  # uses Skroot Laboratory
        pdf.output(f'{location}/Summary.pdf', 'F')  # saves the plot, F refers to file
    except:
        logger.exception("Failed to generate summary PDF")


def checkIfNewPage(pdf, currentX, currentY, labelHeight, plotHeight, paddingX, oldX, labelWidth):
    if currentY >= 1.06 - (labelHeight + plotHeight):
        currentY = paddingX
    else:
        currentX = oldX
    if currentX >= 1.06 - labelWidth:
        currentX = paddingX
        pdf.add_page()
    return currentX, currentY
