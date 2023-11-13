import PyPDF2, re, os


class Importation:
    """
    Used to transform a DI file into a readable file for Plastiveda.

    :param pdf_file_path: A path for the DI pdf file from plastiveda

    """
    def __init__(self, pdf_file_path):
        self.DI = None
        self.registration_date = None
        self.header = {
            'vlme': None,
            'freight' : None,
            'cif' : None,
            'others_expenses' : None,
            'import_tax' : None,
            'ipi' : None,
            'icms' : None,
            'pis' : None,
            'cofins' : None,
            'siscomex_fee' : None,
            'afrmm' : None,
            'exchange_rate_dolar' : None
        }
        self.addictions = {}

        self.firstTime = True

        with open(pdf_file_path, 'rb') as pdf_file:
            os.system('cls')
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            # Getting the number of pages
            self.total_pages = len(pdf_reader.pages)

            for num_page in range(self.total_pages):
                page = pdf_reader.pages[num_page]

                page_text = page.extract_text().replace('\n', ';')

                page_text = self.fixBuggedPage(page_text)
                page_text = self.fixLastLine(page_text)

                if not (self.DI and self.registration_date):
                    self.DI = re.findall(r'Declaração: (\S+)',page_text)[0]
                    self.registration_date = re.findall(r'Data do Registro: (\S+)',page_text)[0]
                    
                addition = re.search(r'Adição: ' + self.DI + r' / ([0-9]{3})',page_text)

                if not addition:
                    vlme_search = re.findall(r'VMLE\.+: \S+ \S+ R\$ (\S+);',page_text)
                    if vlme_search and not self.header['vlme']:
                        self.header['vlme'] = float(str(vlme_search[0]).replace('.','').replace(',','.'))

                    freight_search = re.findall(r'FRETE\.+: \S+ \S+ R\$ (\S+);',page_text)
                    if freight_search and not self.header['freight']:
                        self.header['freight'] = float(str(freight_search[0]).replace('.','').replace(',','.'))

                    cif_search = re.findall(r'Valor CIF Reais\.+: (\S+);', page_text)
                    if cif_search and not self.header['cif']:
                        self.header['cif'] = float(str(cif_search[0]).replace('.','').replace(',','.'))

                    if self.header['cif'] and self.header['freight'] and self.header['vlme'] and vlme_search and freight_search and cif_search:
                        self.header['others_expenses'] = round(self.header['cif'] - (self.header['vlme'] + self.header['freight']),2)

                    import_tax_search = re.findall(r'II\.+: (\S+);',page_text)
                    if import_tax_search and not self.header['import_tax']:
                        self.header['import_tax'] = float(str(import_tax_search[0]).replace('.','').replace(',','.'))

                    ipi_search = re.findall(r'IPI\.+: (\S+);',page_text)
                    if ipi_search and not self.header['ipi']:
                        self.header['ipi'] = float(str(ipi_search[0]).replace('.','').replace(',','.'))

                    icms_search = re.findall(r'ICMS\.+: (\S+);',page_text)
                    if icms_search and not self.header['icms']:
                        self.header['icms'] = float(str(icms_search[0]).replace('.','').replace(',','.'))

                    pis_search = re.findall(r'PIS/PASEP\.+: (\S+);',page_text)
                    if pis_search and not self.header['pis']:
                        self.header['pis'] = float(str(pis_search[0]).replace('.','').replace(',','.'))

                    cofins_search = re.findall(r'COFINS\.+: (\S+);',page_text)
                    if cofins_search and not self.header['cofins']:
                        self.header['cofins'] = float(str(cofins_search[0]).replace('.','').replace(',','.'))

                    siscomex_fee_search = re.findall(r'Taxa Siscomex\.+: (\S+);',page_text)
                    if siscomex_fee_search and not self.header['siscomex_fee']:
                        self.header['siscomex_fee'] = float(str(siscomex_fee_search[0]).replace('.','').replace(',','.'))

                    afrmm_search = re.findall(r'VALOR AFRMM\.+: R\$ (\S+);',page_text)
                    if afrmm_search and not self.header['afrmm']:
                        self.header['afrmm'] = float(str(afrmm_search[0]).replace('.','').replace(',','.'))

                    exchange_rate_dolar_search = re.findall(r'TAXA CAMBIAL\.+: (\S+)',page_text)
                    if exchange_rate_dolar_search and not self.header['exchange_rate_dolar']:
                        self.header['exchange_rate_dolar'] = float(str(exchange_rate_dolar_search[0]).replace('.','').replace(',','.'))

                else:
                    addition = addition.group(1)

                    ncm_addiction = re.findall(r'NBM (\S+);',page_text)[0]
                    vcmv_addiction = float(str(re.findall(r'VCMV: (\S+)',page_text)[0]).replace('.', '').replace(',','.'))
                    net_weight_addiction = float(str(re.findall(r'Peso L.quido da Adi..o: (\S+)',page_text)[0]).replace('.', '').replace(',','.'))

                    #Taxes
                    import_tax_rate_addiction = re.findall(r'Imposto de Importação;Regime de Tributação: .*?\(TEC\): (\S+?)%',page_text)
                    import_tax_value_addiction = None

                    if import_tax_rate_addiction:
                        import_tax_rate_addiction = float(str(import_tax_rate_addiction[0]).replace('.', '').replace(',','.'))

                        import_tax_value_addiction = float(str(re.findall(r'Imposto de Importação;.+?;.+?;Valor a Recolher: R\$ (\S+);',page_text)[0]).replace('.', '').replace(',','.'))
                    else:
                        import_tax_rate_addiction = float(0)
                        import_tax_value_addiction = float(0)

                    ipi_tax_rate_addiction = float(str( re.findall(r'Imposto sobre Produtos Industrializados;.*?;Alíquota Advalorem \(TIPI\) (\S+)%',page_text)[0]).replace('.', '').replace(',','.'))

                    ipi_value_addiction = float(str( re.findall(r'Imposto sobre Produtos Industrializados;Regime de Tributação: .*?;Valor a Recolher: R\$ (\S+);',page_text)[0]).replace('.', '').replace(',','.'))

                    pis_tax_rate_addiction = float(str( re.findall(r'Pis/Pasep;Al.quota AdValorem: (\S+?)%',page_text)[0]).replace('.', '').replace(',','.'))

                    pis_value_addiction = float(str( re.findall(r'Pis/Pasep;Al.quota AdValorem: \S+?%;Valor Devido: R\$ \S+?;Valor a Recolher: R\$ (\S+?);',page_text)[0]).replace('.', '').replace(',','.'))

                    cofins_tax_rate_addiction = float(str( re.findall(r'Cofins;Al.quota AdValorem: (\S+?)%',page_text)[0]).replace('.', '').replace(',','.'))

                    cofins_value_rate_addiction = float(str( re.findall(r'Cofins;Al.quota AdValorem: \S+?%;Valor Devido: R\$ \S+?;Valor a Recolher: R\$ (\S+?);',page_text)[0]).replace('.', '').replace(',','.'))

                    self.addictions[addition] = {
                        'ncm': ncm_addiction,
                        'net_weight': net_weight_addiction, 
                        'values': {
                            'dolar': vcmv_addiction,
                            'real': vcmv_addiction * self.header['exchange_rate_dolar']
                        },
                        'taxes': {
                            'I.I': import_tax_value_addiction,
                            'I.I_fee': import_tax_rate_addiction,
                            'IPI': ipi_value_addiction,
                            'IPI_fee': ipi_tax_rate_addiction,
                            'PIS': pis_value_addiction,
                            'PIS_fee': pis_tax_rate_addiction,
                            'COFINS': cofins_value_rate_addiction,
                            'COFINS_fee': cofins_tax_rate_addiction
                        },
                        'items': {}
                    }
                    #itens
                    quantity_items = re.findall(r'Qtde: (\S+) \S+',page_text)
                    products_codes = re.findall(r'[a-zA-Z]{3}[0-9]{7,12}',page_text)
                    products_descriptions = re.findall(r'[a-zA-Z]{3}[0-9]{7,12} - (.+?);',page_text)
                    products_values = re.findall(r'Qtde: \S+ \S+ \S+ (\S+)',page_text)

                    total_items_addiction = len(products_codes)

                    for x in range(total_items_addiction):
                        
                        self.addictions[addition]['items'][x + 1] = {
                            'code': products_codes[x],
                            'description': products_descriptions[x],
                            'quantity': float(str(quantity_items[x]).replace('.','').replace(',','.')),
                            'value': round(float(str(products_values[x]).replace('.','').replace(',','.')) * self.header['exchange_rate_dolar'],2),
                        }
        print()
        self.getInvoice()  


    def fixBuggedPage(self, page_text):
        """ Take a page text from a 
        """
        lineBugged = re.findall(r';(\w+\.+;.+?;)',page_text)
        if lineBugged:
            lineBugged = lineBugged[0]
            text = re.sub(r';','',lineBugged)
            new_page_text = re.sub(lineBugged,f';{text};', page_text)
            return new_page_text
        
        return page_text
    
    def fixLastLine (self, page_text):
        last_line = re.search(r'Declaração: (.+)',page_text)
        if last_line:
            last_line = last_line.group()
            new_page_text = re.sub(last_line, f';{last_line}',page_text)
            return new_page_text
        
        return page_text

    def getInvoice(self):

        # cabeçalho (usa os tamanhos das colunas)
        cols_sizes = {'col1_size': 26, 'col2_size': 26, 'col3_size': 26}
        format_header = '{:{col1_size}} {:<{col2_size}} {:>{col3_size}}'
        print(f'{"RELATÓRIO DA INVOICE ":^70}')
        print('-' * 80)
        print('-' * 80)
        print(format_header.format('FRETE', 'DESPESAS', 'VLME', **cols_sizes))
        # print('-' * 80)

        format_data = '{:<{col1_size}} {:<{col2_size}} {:>{col3_size}}'
        print(format_data.format(self.format_value_header('freight'), self.format_value_header('others_expenses'), self.format_value_header('vlme'), **cols_sizes))

        print('=' * 80)
        print(f"{'Total (CIF): ' + self.format_value_header('cif'):>80}")

        print()
        print()
        print()

        cols_sizes_taxes = {'col1_size': 16, 'col2_size': 16, 'col3_size': 16, 'col4_size': 16, 'col5_size': 16}
        formato_taxes = '{:<{col1_size}} {:<{col2_size}} {:^{col3_size}} {:>{col4_size}} {:>{col5_size}}'
        print(f'{"IMPOSTOS ":^84}')
        print('-' * 84)
        print('-' * 84)
        print(formato_taxes.format('I.I', 'IPI', 'ICMS','PIS', 'COFINS', ** cols_sizes_taxes))
        print(formato_taxes.format(self.format_value_header('import_tax'), self.format_value_header('ipi'), self.format_value_header('icms'), self.format_value_header('pis'), self.format_value_header('cofins'), **cols_sizes_taxes))
        print('=' * 84)
        print(f"{'Total (R$): ' + str((self.format_value(self.header['import_tax'] + self.header['ipi'] + self.header['icms'] + self.header['pis'] + self.header['cofins']))):>84}")
        print()
        print()
        print()

        cols_sizes_others = {'col1_size': 15, 'col2_size': 15}
        format_others = '{:<{col1_size}} {:>{col2_size}}'
        print(f'{"OUTROS ":^30}')
        print('-' * 31)
        print('-' * 31)
        print(format_others.format('AFRMM', 'SISCOMEX', ** cols_sizes_others))
        print(format_others.format(self.format_value_header('afrmm'), self.format_value_header('siscomex_fee'), **cols_sizes_others))
        print('=' * 31)
        print(f"{'Total (R$): ' + str((self.format_value(self.header['afrmm'] + self.header['siscomex_fee']))):>31}")
        print()
        print()
        print()

        cols_sizes_total = {'col1_size': 15, 'col2_size': 15, 'col3_size': 15}
        format_total = '{:<{col1_size}} {:^{col2_size}} {:>{col3_size}}'
        print(f'{"TOTAL NOTA ":^50}')
        print('-' * 47)
        print('-' * 47)
        print(format_total.format('CIF', 'IMPOSTOS', 'OUTROS', ** cols_sizes_total))
        print(format_total.format(self.format_value_header('cif'), self.getTotalTax(), self.getTotalOthers(), ** cols_sizes_total))
        print('=' * 47)
        print(f"{'Total (R$): ' + str((self.format_value(self.getTotalValueNF()))):>31}")
        print()
        print()

        cols_sizes_addictions_header = {'col1_size': 90, 'col2_size': 90}
        cols_sizes_addictions_items = {'col1_size': 20, 'col2_size': 50, 'col3_size': 15, 'col4_size': 15, 'col5_size': 15, 'col6_size': 13, 'col7_size': 11, 'col8_size': 15, 'col9_size': 15}

        format_addictions_header = '{:^{col1_size}} {:^{col2_size}}'
        format_addictions_item = '{:<{col1_size}} {:<{col2_size}} {:>{col3_size}} {:>{col4_size}} {:>{col5_size}} {:>{col6_size}} {:>{col7_size}} {:>{col8_size}} {:>{col9_size}}'
        print(f'{"Adições": ^177}')
        print('-' * 177)
        print('-' * 177)
        for addiction in self.addictions:
            print(f'{addiction:^177}')
            print('-' * 177) 
            # print(f'{self.addictions[addiction]["ncm"]:^80}')
            print(format_addictions_header.format(self.addictions[addiction]['ncm'], self.get_net_weight(addiction), ** cols_sizes_addictions_header))
            print('-' * 177) 
            print(format_addictions_item.format('Código', 'Descricao','Quant','V. Unitario','Valor Total','I.I','IPI','PIS','COFINS' ,** cols_sizes_addictions_items))
            for item in self.addictions[addiction]['items']:
                print(format_addictions_item.format(
                    self.addictions[addiction]['items'][item]['code'], 
                    self.addictions[addiction]['items'][item]['description'][:50],
                    self.addictions[addiction]['items'][item]['quantity'], 
                    self.format_value(self.addictions[addiction]['items'][item]['value']), 
                    self.format_value(self.addictions[addiction]['items'][item]['value'] * self.addictions[addiction]['items'][item]['quantity']), 
                    self.get_item_addiction_ii(addiction,item), 
                    self.get_item_addiction_IPI(addiction,item),
                    self.get_item_addiction_PIS(addiction,item),
                    self.get_item_addiction_COFINS(addiction,item),
                    ** cols_sizes_addictions_items))
            print('=' * 177) 
            print(format_addictions_item.format(
                    '', 
                    '',
                    '', 
                    '', 
                    self.get_total(addiction), 
                    self.format_value(self.addictions[addiction]['taxes']['I.I']), 
                    self.format_value(self.addictions[addiction]['taxes']['IPI']),
                    self.format_value(self.addictions[addiction]['taxes']['PIS']),
                    self.format_value(self.addictions[addiction]['taxes']['COFINS']),
                    ** cols_sizes_addictions_items))
            print(format_addictions_item.format(
                    '', 
                    '',
                    '', 
                    '', 
                    '', 
                    self.addictions[addiction]['taxes']['I.I_fee'], 
                    self.addictions[addiction]['taxes']['IPI_fee'],
                    self.addictions[addiction]['taxes']['PIS_fee'],
                    self.addictions[addiction]['taxes']['COFINS_fee'],
                    ** cols_sizes_addictions_items))
            print('/' * 177)
            print()

            cols_sizes_addictions_summurized = {'col1_size': 10, 'col2_size': 20, 'col3_size': 20, 'col4_size': 20, 'col5_size': 20, 'col6_size': 20, 'col7_size': 20, 'col8_size': 20}
            format_addictions_header_summurized = '{:^{col1_size}} {:<{col2_size}} {:<{col3_size}} {:<{col4_size}} {:<{col5_size}} {:<{col6_size}} {:<{col7_size}} {:<{col8_size}}'
        print(f'{"ADIÇÕES RESUMIDO": ^150}')
        print('-' * 150) 
        print(format_addictions_header_summurized.format(
                'ADICAO',
                'NCM',
                'PESO',
                'VALOR', 
                'I.I',
                'IPI', 
                'PIS', 
                'COFINS', 
                ** cols_sizes_addictions_summurized))
        for addiction in self.addictions:
            print(format_addictions_header_summurized.format(
                    addiction,
                    self.addictions[addiction]['ncm'],
                    self.get_net_weight(addiction),
                    self.get_total(addiction), 
                    self.format_value(self.addictions[addiction]['taxes']['I.I']),
                    self.format_value(self.addictions[addiction]['taxes']['IPI']), 
                    self.format_value(self.addictions[addiction]['taxes']['PIS']), 
                    self.format_value(self.addictions[addiction]['taxes']['COFINS']), 
                    ** cols_sizes_addictions_summurized))
        print('=' * 150)
        print(format_addictions_header_summurized.format(
                    '',
                    '',
                    self.get_total_net_weight(),
                    self.format_value(self.header['cif']), 
                    self.format_value(self.header['import_tax']),
                    self.format_value(self.header['ipi']), 
                    self.format_value(self.header['pis']), 
                    self.format_value(self.header['cofins']), 
                    ** cols_sizes_addictions_summurized))
        print()
        print()
        print()



    def format_value_header(self, param):
        return ("R$ {0:,.2f}".format(self.header[param]).replace('.',';').replace(',','.').replace(';',','))
    
    def format_value(self, value):
        return ("R$ {0:,.2f}".format(value).replace('.',';').replace(',','.').replace(';',','))
    
    def getTotalTax(self):
        return ("R$ {0:,.2f}".format((self.header['import_tax'] + self.header['ipi'] + self.header['icms'] + self.header['pis'] + self.header['cofins'])).replace('.',';').replace(',','.').replace(';',','))
    
    def getTotalOthers(self):
        return ("R$ {0:,.2f}".format((self.header['afrmm'] + self.header['siscomex_fee'])).replace('.',';').replace(',','.').replace(';',','))
    
    def getTotalValueNF(self):
        return (self.header['cif'] + self.header['import_tax'] + self.header['ipi'] + self.header['icms'] + self.header['pis'] + self.header['cofins'] + self.header['afrmm'] + self.header['siscomex_fee'])
    
    def get_net_weight(self, addiction):
        return (str(self.addictions[addiction]['net_weight']).replace(',',';').replace('.',',').replace(';','.') + ' KG')
    
    def get_total_net_weight(self):
        net_weight = 0
        for addiction in self.addictions:
            net_weight += self.addictions[addiction]['net_weight']
        return (str(round(net_weight,2)).replace(',',';').replace('.',',').replace(';','.') + ' KG')
    
    def get_item_addiction_taxes(self, addiction):
        return (str(self.addictions[addiction]['taxes']).replace(',',';').replace('.',',').replace(';','.') + ' KG')
    
    def get_item_addiction_ii(self, addiction, item):
        return self.format_value(
            self.addictions[addiction]['items'][item]['value'] * self.addictions[addiction]['items'][item]['quantity'] * self.addictions[addiction]['taxes']['I.I_fee'] / 100
        )
    def get_item_addiction_IPI(self, addiction, item):
        return self.format_value(
            ((self.addictions[addiction]['items'][item]['value'] * self.addictions[addiction]['items'][item]['quantity']) + self.addictions[addiction]['items'][item]['value'] * self.addictions[addiction]['items'][item]['quantity'] * self.addictions[addiction]['taxes']['I.I_fee'] / 100) * self.addictions[addiction]['taxes']['IPI_fee'] / 100
        )
    
    def get_item_addiction_PIS(self, addiction, item):
        return self.format_value(
            self.addictions[addiction]['items'][item]['value'] * self.addictions[addiction]['items'][item]['quantity'] * self.addictions[addiction]['taxes']['PIS_fee'] / 100
        )
    
    def get_item_addiction_COFINS(self, addiction, item):
        return self.format_value(
            self.addictions[addiction]['items'][item]['value'] * self.addictions[addiction]['items'][item]['quantity'] * self.addictions[addiction]['taxes']['COFINS_fee'] / 100
        )
    
    def get_total(self, addiction):
        total = 0
        for item in self.addictions[addiction]['items']:
            total += (self.addictions[addiction]['items'][item]['value'] * self.addictions[addiction]['items'][item]['quantity'])
        return self.format_value(total)

test = Importation('1111.pdf')