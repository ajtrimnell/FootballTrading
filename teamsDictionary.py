''' Rapid Api on left and Betfair on right'''

teamsDictionary = {
    "leagues":	{	
        39:{	
            "Arsenal":"Arsenal",
            "Aston Villa":"Aston Villa",
            "Bournemouth":"Bournemouth",
            "Brentford":"Brentford",
            "Brighton":"Brighton",
            "Burnley":"Burnley",
            "Chelsea":"Chelsea",
            "Crystal Palace":"Crystal Palace",
            "Everton":"Everton",
            "Fulham":"Fulham",
            "Liverpool":"Liverpool",
            "Luton":"Luton",
            "Manchester City":"Man City",
            "Manchester United":"Man Utd",
            "Newcastle":"Newcastle",
            "Nottingham Forest":"Nottm Forest",
            "Sheffield Utd":"Sheff Utd",
            "Tottenham":"Tottenham",
            "West Ham":"West Ham",
            "Wolves":"Wolves"
        },	
        40:{	
            "Birmingham":"Birmingham",
            "Blackburn":"Blackburn",
            "Bristol City":"Bristol City",
            "Cardiff":"Cardiff",
            "Coventry":"Coventry",
            "Huddersfield":"Huddersfield",
            "Hull City":"Hull",
            "Ipswich":"Ipswich",
            "Leeds":"Leeds",
            "Leicester":"Leicester",
            "Middlesbrough":"Middlesbrough",
            "Millwall":"Millwall",
            "Norwich":"Norwich",
            "Plymouth":"Plymouth",
            "Preston":"Preston",
            "QPR":"QPR",
            "Rotherham":"Rotherham",
            "Sheffield Wednesday":"Sheff Wed",
            "Southampton":"Southampton",
            "Stoke City":"Stoke",
            "Sunderland":"Sunderland",
            "Swansea":"Swansea",
            "Watford":"Watford",
            "West Brom":"West Brom"
        },	
        41:{	
            "Barnsley":"Barnsley",
            "Blackpool":"Blackpool",
            "Bolton":"Bolton",
            "Bristol Rovers":"Bristol Rovers",
            "Burton Albion":"Burton Albion",
            "Cambridge United":"Cambridge Utd",
            "Carlisle":"Carlisle",
            "Charlton":"Charlton",
            "Cheltenham":"Cheltenham",
            "Derby":"Derby",
            "Exeter City":"Exeter",
            "Fleetwood Town":"Fleetwood Town",
            "Leyton Orient":"Leyton Orient",
            "Lincoln":"Lincoln",
            "Northampton":"Northampton",
            "Oxford United":"Oxford Utd",
            "Peterborough":"Peterborough",
            "Port Vale":"Port Vale",
            "Portsmouth":"Portsmouth",
            "Reading":"Reading",
            "Shrewsbury":"Shrewsbury",
            "Stevenage":"Stevenage",
            "Wigan":"Wigan",
            "Wycombe":"Wycombe"
        },	
        41:{
            "AFCWimbledon":"AFC Wimbledon",
            "AccringtonST":"Accrington",
            "Barrow":"Barrow",
            "Bradford":"Bradford",
            "Colchester":"Colchester",
            "CrawleyTown":"Crawley",
            "Crewe":"Crewe",
            "Doncaster":"Doncaster",
            "ForestGreen":"Forest Green",
            "Gillingham":"Gillingham",
            "Grimsby":"Grimsby",
            "HarrogateTown":"Harrogate Town",
            "MansfieldTown":"Mansfield",
            "MiltonKeynesDons":"MK Dons",
            "Morecambe":"Morecambe",
            "NewportCounty":"Newport County",
            "NottsCounty":"Notts Co",
            "SalfordCity":"Salford City",
            "StockportCounty":"Stockport",
            "SuttonUtd":"Sutton Utd",
            "SwindonTown":"Swindon",
            "Tranmere":"Tranmere",
            "Walsall":"Walsall",
            "Wrexham":"Wrexham"
        },
        43: {
            "AFC Fylde":"AFC Fylde",
            "Aldershot Town":"Aldershot",
            "Altrincham":"Altrincham",
            "Barnet":"Barnet",
            "Boreham Wood":"Boreham Wood",
            "Bromley":"Bromley",
            "Chesterfield":"Chesterfield",
            "Dagenham & Redbridge":"Dag and Red",
            "Dorking Wanderers":"Dorking Wanderers",
            "Eastleigh":"Eastleigh",
            "Ebbsfleet United":"Ebbsfleet Utd",
            "FC Halifax Town":"FC Halifax Town",
            "Gateshead":"Gateshead",
            "Hartlepool":"Hartlepool",
            "Kidderminster Harriers":"Kidderminster",
            "Maidenhead":"Maidenhead",
            "Oldham":"Oldham",
            "Oxford City":"Oxford City",
            "Rochdale":"Rochdale",
            "Solihull Moors":"Solihull Moors",
            "Southend":"Southend",
            "Wealdstone":"Wealdstone",
            "Woking":"Woking",
            "York":"York City"
        },
        140:{	
            "Alaves":"Alaves",
            "Almeria":"Almeria",
            "Athletic Club":"Athletic Bilbao",
            "Atletico Madrid":"Atletico Madrid",
            "Barcelona":"Barcelona",
            "Cadiz":"Cadiz",
            "Celta Vigo":"Celta Vigo",
            "Getafe":"Getafe",
            "Girona":"Girona",
            "Granada CF":"Granada",
            "Las Palmas":"Las Palmas",
            "Mallorca":"Mallorca",
            "Osasuna":"Osasuna",
            "Rayo Vallecano":"Rayo Vallecano",
            "Real Betis":"Betis",
            "Real Madrid":"Real Madrid",
            "Real Sociedad":"Real Sociedad",
            "Sevilla":"Sevilla",
            "Valencia":"Valencia",
            "Villarreal":"Villarreal"
        },	
        141:{
            "Amorebieta":"Albacete",
            "Burgos":"Burgos",
            "Eibar":"Eibar",
            "Elche":"Elche",
            "Eldense":"Eldense",
            "Espanyol":"Espanyol",
            "FCAndorra":"FC Andorra",
            "FCCartagena":"FC Cartagena",
            "Huesca":"Huesca",
            "Leganes":"Leganes",
            "Levante":"Levante",
            "Mirandes":"Mirandes",
            "Oviedo":"Oviedo",
            "RacingFerrol":"Racing de Ferrol",
            "RacingSantander":"Racing Santander",
            "SportingGijon":"Sporting Gijon",
            "Tenerife":"Tenerife",
            "Valladolid":"Valladolid",
            "VillarrealII":"Villarreal II",
            "Zaragoza":"Zaragoza"
        },
        135:{	
            "AC Milan":"AC Milan",
            "AS Roma":"Roma",
            "Atalanta":"Atalanta",
            "Bologna":"Bologna",
            "Cagliari":"Cagliari",
            "Empoli":"Empoli",
            "Fiorentina":"Fiorentina",
            "Frosinone":"Frosinone",
            "Genoa":"Genoa",
            "Inter":"Inter",
            "Juventus":"Juventus",
            "Lazio":"Lazio",
            "Lecce":"Lecce",
            "Monza":"AC Monza",
            "Napoli":"Napoli",
            "Salernitana":"Salernitana",
            "Sassuolo":"Sassuolo",
            "Torino":"Torino",
            "Udinese":"Udinese",
            "Verona":"Verona"
        },	
        78:{	
            "1.FC Köln":"FC Koln",
            "1899 Hoffenheim":"Hoffenheim",
            "Bayer Leverkusen":"Leverkusen",
            "Bayern Munich":"Bayern Munich",
            "Borussia Dortmund":"Dortmund",
            "Borussia Monchengladbach":"Mgladbach",
            "Eintracht Frankfurt":"Eintracht Frankfurt",
            "FC Augsburg":"Augsburg",
            "FC Heidenheim":"FC Heidenheim",
            "FSV Mainz 05":"Mainz",
            "RB Leipzig":"RB Leipzig",
            "SC Freiburg":"Freiburg",
            "SV Darmstadt 98":"SV Darmstadt",
            "Union Berlin":"Union Berlin",
            "VfB Stuttgart":"Stuttgart",
            "Vfl Bochum":"Bochum",
            "VfL Wolfsburg":"Wolfsburg",
            "Werder Bremen":"Bremen"
        },
        61:{	
            "Clermont Foot":"Clermont",
            "Le Havre":"Le Havre",
            "Lens":"Lens",
            "Lille":"Lille",
            "Lorient":"Lorient",
            "Lyon":"Lyon",
            "Marseille":"Marseille",
            "Metz":"Metz",
            "Monaco":"Monaco",
            "Montpellier":"Montpellier",
            "Nantes":"Nantes",
            "Nice":"Nice",
            "Paris Saint Germain":"Paris St-G",
            "Reims":"Reims",
            "Rennes":"Rennes",
            "Stade Brestois 29":"Brest",
            "Strasbourg":"Strasbourg",
            "Toulouse":"Toulouse"
        }	
    }		
}