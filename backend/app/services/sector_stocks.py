"""Top constituent stocks per sector ETF — used for sub-sector treemap."""

STOCK_NAMES: dict[str, str] = {
    # Financials (금융)
    "JPM": "JPMorgan Chase", "BRK-B": "Berkshire Hathaway", "V": "Visa", "MA": "Mastercard",
    "BAC": "Bank of America", "WFC": "Wells Fargo", "GS": "Goldman Sachs", "MS": "Morgan Stanley",
    "SPGI": "S&P Global", "AXP": "American Express", "BLK": "BlackRock", "C": "Citigroup",
    "MMC": "Marsh & McLennan", "CB": "Chubb", "SCHW": "Charles Schwab", "BK": "BNY Mellon",
    "STT": "State Street", "USB": "U.S. Bancorp", "PNC": "PNC Financial", "AON": "Aon",

    # Real Estate (부동산)
    "PLD": "Prologis", "AMT": "American Tower", "EQIX": "Equinix", "CCI": "Crown Castle",
    "PSA": "Public Storage", "O": "Realty Income", "WELL": "Welltower", "DLR": "Digital Realty",
    "SPG": "Simon Property", "VICI": "VICI Properties", "AVB": "AvalonBay", "EQR": "Equity Residential",
    "CBRE": "CBRE Group", "WY": "Weyerhaeuser", "ARE": "Alexandria Real Estate", "IRM": "Iron Mountain",
    "EXR": "Extra Space Storage", "SBAC": "SBA Communications", "BXP": "Boston Properties", "MAA": "Mid-America Apartment",

    # Technology (기술)
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AVGO": "Broadcom",
    "CRM": "Salesforce", "ADBE": "Adobe", "AMD": "AMD", "CSCO": "Cisco",
    "ORCL": "Oracle", "ACN": "Accenture", "INTC": "Intel", "IBM": "IBM",
    "INTU": "Intuit", "TXN": "Texas Instruments", "QCOM": "Qualcomm", "AMAT": "Applied Materials",
    "MU": "Micron Technology", "LRCX": "Lam Research", "NOW": "ServiceNow", "PANW": "Palo Alto Networks",

    # Consumer Discretionary (임의소비재)
    "AMZN": "Amazon", "TSLA": "Tesla", "HD": "Home Depot", "MCD": "McDonald's",
    "NKE": "Nike", "LOW": "Lowe's", "SBUX": "Starbucks", "TJX": "TJX Companies",
    "BKNG": "Booking Holdings", "CMG": "Chipotle", "MAR": "Marriott", "ORLY": "O'Reilly Automotive",
    "LULU": "Lululemon", "DASH": "DoorDash", "AZO": "AutoZone", "F": "Ford",
    "GM": "General Motors", "HLT": "Hilton", "YUM": "Yum! Brands", "ABNB": "Airbnb",

    # Industrials (산업재)
    "CAT": "Caterpillar", "UNP": "Union Pacific", "HON": "Honeywell", "GE": "GE Aerospace",
    "RTX": "RTX Corporation", "DE": "Deere & Co", "BA": "Boeing", "LMT": "Lockheed Martin",
    "UPS": "UPS", "ADP": "Automatic Data Processing", "MMM": "3M", "WM": "Waste Management",
    "EMR": "Emerson Electric", "ITW": "Illinois Tool Works", "NSC": "Norfolk Southern", "ETN": "Eaton",
    "PH": "Parker-Hannifin", "FDX": "FedEx", "GD": "General Dynamics", "NOC": "Northrop Grumman",

    # Materials (소재)
    "LIN": "Linde", "APD": "Air Products", "SHW": "Sherwin-Williams", "ECL": "Ecolab",
    "FCX": "Freeport-McMoRan", "NUE": "Nucor", "NEM": "Newmont", "DD": "DuPont",
    "DOW": "Dow Inc", "VMC": "Vulcan Materials", "MLM": "Martin Marietta", "PPG": "PPG Industries",
    "ALB": "Albemarle", "CF": "CF Industries", "MOS": "Mosaic", "FMC": "FMC Corp",
    "IFF": "International Flavors & Fragrances", "BALL": "Ball Corp", "CE": "Celanese", "CTVA": "Corteva",

    # Energy (에너지)
    "XOM": "ExxonMobil", "CVX": "Chevron", "COP": "ConocoPhillips", "EOG": "EOG Resources",
    "SLB": "Schlumberger", "MPC": "Marathon Petroleum", "PXD": "Pioneer Natural Resources", "PSX": "Phillips 66",
    "VLO": "Valero Energy", "OXY": "Occidental Petroleum", "HES": "Hess", "WMB": "Williams Companies",
    "HAL": "Halliburton", "BKR": "Baker Hughes", "FANG": "Diamondback Energy", "KMI": "Kinder Morgan",
    "TRGP": "Targa Resources", "DVN": "Devon Energy", "MRO": "Marathon Oil", "APA": "APA Corp",

    # Utilities (유틸리티)
    "NEE": "NextEra Energy", "SO": "Southern Company", "DUK": "Duke Energy", "CEG": "Constellation Energy",
    "SRE": "Sempra", "AEP": "American Electric Power", "D": "Dominion Energy", "EXC": "Exelon",
    "PCG": "PG&E", "XEL": "Xcel Energy", "WEC": "WEC Energy", "ED": "Consolidated Edison",
    "PEG": "Public Service Enterprise", "ETR": "Entergy", "FE": "FirstEnergy", "PPL": "PPL Corp",
    "AEE": "Ameren", "LNT": "Alliant Energy", "ATO": "Atmos Energy", "NI": "NiSource",

    # Healthcare (헬스케어)
    "UNH": "UnitedHealth", "JNJ": "Johnson & Johnson", "LLY": "Eli Lilly", "PFE": "Pfizer",
    "ABT": "Abbott", "TMO": "Thermo Fisher", "MRK": "Merck", "ABBV": "AbbVie",
    "DHR": "Danaher", "BMY": "Bristol Myers Squibb", "AMGN": "Amgen", "MDT": "Medtronic",
    "ISRG": "Intuitive Surgical", "GILD": "Gilead Sciences", "VRTX": "Vertex", "REGN": "Regeneron",
    "SYK": "Stryker", "ELV": "Elevance Health", "BSX": "Boston Scientific", "HUM": "Humana",

    # Consumer Staples (필수소비재)
    "PG": "Procter & Gamble", "KO": "Coca-Cola", "PEP": "PepsiCo", "COST": "Costco",
    "WMT": "Walmart", "PM": "Philip Morris", "MO": "Altria", "MDLZ": "Mondelez",
    "CL": "Colgate-Palmolive", "KMB": "Kimberly-Clark", "GIS": "General Mills", "STZ": "Constellation Brands",
    "SYY": "Sysco", "ADM": "Archer-Daniels-Midland", "TGT": "Target", "EL": "Estee Lauder",
    "K": "Kellanova", "HRL": "Hormel Foods", "KR": "Kroger", "DG": "Dollar General",

    # Communication Services (통신)
    "GOOGL": "Alphabet (Class A)", "META": "Meta Platforms", "NFLX": "Netflix", "DIS": "Disney",
    "CMCSA": "Comcast", "T": "AT&T", "VZ": "Verizon", "TMUS": "T-Mobile",
    "CHTR": "Charter Communications", "EA": "Electronic Arts", "WBD": "Warner Bros. Discovery", "TTWO": "Take-Two",
    "LYV": "Live Nation", "PARA": "Paramount", "SNAP": "Snap Inc", "MTCH": "Match Group",
    "ROKU": "Roku", "GOOG": "Alphabet (Class C)", "PINS": "Pinterest", "OMC": "Omnicom",
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
