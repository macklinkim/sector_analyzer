"""Top constituent stocks per sector ETF — used for sub-sector treemap."""

STOCK_NAMES: dict[str, str] = {
    # Financials
    "JPM": "JPMorgan", "BRK-B": "Berkshir", "V": "Visa", "MA": "Mastercd",
    "BAC": "BofA", "WFC": "WellsFrg", "GS": "Goldman", "MS": "MorganSt",
    "SPGI": "S&PGlbl", "AXP": "AmExprss", "BLK": "BlackRck", "C": "Citi",
    "MMC": "MarshMcL", "CB": "Chubb", "SCHW": "Schwab",
    # Real Estate
    "PLD": "Prolgis", "AMT": "AmTower", "EQIX": "Equinix", "CCI": "CrwnCstl",
    "PSA": "PubStrge", "O": "Realty", "WELL": "Welltwr", "DLR": "DigtlRty",
    "SPG": "SimonPrp", "VICI": "VICI Prp", "AVB": "AvnBay", "EQR": "EqtyRes",
    # Technology
    "AAPL": "Apple", "MSFT": "Microso", "NVDA": "Nvidia", "AVGO": "Broadcom",
    "CRM": "Salesfrc", "ADBE": "Adobe", "AMD": "AMD", "CSCO": "Cisco",
    "ORCL": "Oracle", "ACN": "Accentr", "INTC": "Intel", "IBM": "IBM",
    "INTU": "Intuit", "TXN": "TexasIns", "QCOM": "Qualcomm",
    # Consumer Discretionary
    "AMZN": "Amazon", "TSLA": "Tesla", "HD": "HomeDpt", "MCD": "McDnlds",
    "NKE": "Nike", "LOW": "Lowes", "SBUX": "Starbck", "TJX": "TJX",
    "BKNG": "Booking", "CMG": "Chiptle", "MAR": "Marriot", "ORLY": "OReilly",
    # Industrials
    "CAT": "Caterpil", "UNP": "UnPacif", "HON": "Honywel", "GE": "GE Aero",
    "RTX": "RTX", "DE": "Deere", "BA": "Boeing", "LMT": "Lockhd",
    "UPS": "UPS", "ADP": "ADP", "MMM": "3M", "WM": "WasteMgt",
    "EMR": "Emerson", "ITW": "IllTool",
    # Materials
    "LIN": "Linde", "APD": "AirProd", "SHW": "SherWin", "ECL": "Ecolab",
    "FCX": "Freeport", "NUE": "Nucor", "NEM": "Newmont", "DD": "DuPont",
    "DOW": "Dow Inc", "VMC": "Vulcan", "MLM": "MartinM", "PPG": "PPG Ind",
    # Energy
    "XOM": "ExxonMb", "CVX": "Chevron", "COP": "ConPhil", "EOG": "EOG Res",
    "SLB": "Schlmbr", "MPC": "Marathn", "PXD": "Pioneer", "PSX": "Phillps",
    "VLO": "Valero", "OXY": "Occidntl", "HES": "Hess", "WMB": "William",
    # Utilities
    "NEE": "NxtEraE", "SO": "Southrn", "DUK": "Duke En", "CEG": "Constel",
    "SRE": "Sempra", "AEP": "AEP", "D": "Dominon", "EXC": "Exelon",
    "PCG": "PG&E", "XEL": "Xcel En", "WEC": "WEC Eng", "ED": "ConEdis",
    # Healthcare
    "UNH": "UnitdHl", "JNJ": "J&J", "LLY": "EliLily", "PFE": "Pfizer",
    "ABT": "Abbott", "TMO": "ThrmoFs", "MRK": "Merck", "ABBV": "AbbVie",
    "DHR": "Danaher", "BMY": "Bristol", "AMGN": "Amgen", "MDT": "Medtrnc",
    "ISRG": "IntSurg", "GILD": "Gilead",
    # Consumer Staples
    "PG": "P&G", "KO": "CocaCla", "PEP": "Pepsi", "COST": "Costco",
    "WMT": "Walmart", "PM": "PhilMor", "MO": "Altria", "MDLZ": "Mondelz",
    "CL": "Colgate", "KMB": "KimClrk", "GIS": "GenMill", "STZ": "Constel",
    # Communication
    "GOOGL": "Alphbet", "META": "Meta", "NFLX": "Netflix", "DIS": "Disney",
    "CMCSA": "Comcast", "T": "AT&T", "VZ": "Verizon", "TMUS": "T-Mobil",
    "CHTR": "Charter", "EA": "EA", "WBD": "WBDiscv", "TTWO": "Take2",
    "LYV": "LiveNtn", "PARA": "Paramnt",
}

SECTOR_CONSTITUENTS: dict[str, list[str]] = {
    "XLF": ["JPM", "BRK-B", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "AXP", "BLK", "C", "MMC", "CB", "SCHW"],
    "XLRE": ["PLD", "AMT", "EQIX", "CCI", "PSA", "O", "WELL", "DLR", "SPG", "VICI", "AVB", "EQR"],
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "CRM", "ADBE", "AMD", "CSCO", "ORCL", "ACN", "INTC", "IBM", "INTU", "TXN", "QCOM"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "CMG", "MAR", "ORLY"],
    "XLI": ["CAT", "UNP", "HON", "GE", "RTX", "DE", "BA", "LMT", "UPS", "ADP", "MMM", "WM", "EMR", "ITW"],
    "XLB": ["LIN", "APD", "SHW", "ECL", "FCX", "NUE", "NEM", "DD", "DOW", "VMC", "MLM", "PPG"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PXD", "PSX", "VLO", "OXY", "HES", "WMB"],
    "XLU": ["NEE", "SO", "DUK", "CEG", "SRE", "AEP", "D", "EXC", "PCG", "XEL", "WEC", "ED"],
    "XLV": ["UNH", "JNJ", "LLY", "PFE", "ABT", "TMO", "MRK", "ABBV", "DHR", "BMY", "AMGN", "MDT", "ISRG", "GILD"],
    "XLP": ["PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "MDLZ", "CL", "KMB", "GIS", "STZ"],
    "XLC": ["GOOGL", "META", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "EA", "WBD", "TTWO", "LYV", "PARA"],
}
