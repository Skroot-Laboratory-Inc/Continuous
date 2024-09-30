import logging

from fpdf import FPDF

from src.app.file_manager.common_file_manager import CommonFileManager


class PDF(FPDF):
    def header(self):
        FileManager = CommonFileManager()
        self.image(FileManager.getSquareLogo(), self.pdf_w - 40, self.pdf_h, 30, self.footerHeight)

    def setFooterHeight(self, footerHeight):
        self.footerHeight = footerHeight
        self.topPadding = 20

    def setPageWidthHeight(self, height, width):
        self.pdf_w = width
        self.pdf_h = height - self.footerHeight

    def drawLine(self, xrel, yrel):
        self.set_line_width(0.0)
        self.line(0, self.pdf_h * yrel, self.pdf_w * xrel, self.pdf_h * yrel)

    def drawCircle(self, xrel, yrel, rrel, color):
        if color == 'green':
            self.set_fill_color(r=26, g=124, b=42)
        else:  # red
            self.set_fill_color(r=129, g=17, b=17)
        self.ellipse(x=self.pdf_w * xrel, y=self.pdf_h * yrel + self.topPadding, w=self.pdf_h * rrel,
                     h=self.pdf_h * rrel, style="FD")

    def placeImage(self, plt, xrel, yrel, relwidth, relheight):
        self.set_xy(self.pdf_w * xrel, self.pdf_h * yrel + self.topPadding)
        self.image(plt, link='', type='', w=relwidth * self.pdf_w, h=relheight * self.pdf_h)

    def placeText(self, text, xrel, yrel, relwidth, relheight, fontsize, bold):
        self.set_xy(self.pdf_w * xrel, self.pdf_h * yrel + self.topPadding)
        if bold:
            self.set_font('Arial', 'B', fontsize)
            self.multi_cell(w=relwidth * self.pdf_w, h=relheight * self.pdf_h, align='C', txt=text, border=0)
        else:
            self.set_font('Arial', '', fontsize)
            self.multi_cell(w=relwidth * self.pdf_w, h=relheight * self.pdf_h, align='L', txt=text, border=0)

    def setAuthor(self):
        self.set_author('Skroot Laboratory')


def generatePdf(Readers, setupFormLocation, summaryPdfLocation):
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.setFooterHeight(30)
    pdf.setPageWidthHeight(210, 297)
    generateIntroPage(pdf, setupFormLocation)
    generateReaderPages(pdf, Readers)
    pdf.setAuthor()  # uses Skroot Laboratory
    pdf.output(summaryPdfLocation, 'F')  # saves the plot, F refers to file


def generateIntroPage(pdf, setupFormLocation):
    pdf.add_page()
    pdf.placeImage(setupFormLocation, 0.03, 0.02, 0.3, 0.3)


def generateReaderPages(pdf, Readers):
    try:
        for Reader in Readers:
            try:
                padding = 0.02
                pdf.add_page()
                Reader.addToPdf(
                    pdf,
                    padding,
                    padding,
                    0.05,
                    1-padding,
                    1-(pdf.footerHeight/pdf.pdf_h)
                )
            except:
                logging.exception(f'Failed to update pdf')
    except:
        logging.exception("Failed to generate summary PDF")
