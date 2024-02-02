# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db
import random
import timedelta, datetime



def connection():
    ''' User this function to create your connections '''
    con = db.connect(host="127.0.0.1", user="root", password="", database="taxidia")
    
    return con

def  findTrips(x,a,b):
    
    # Create a new connection
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    sql1 = """SELECT trip.trip_package_id, trip.cost_per_person, trip.max_num_participants, count(distinct r.Reservation_id), trip.max_num_participants - count(distinct r.Reservation_id),trip.trip_start, trip.trip_end
    FROM trip_package as trip, reservation as r, travel_agency_branch as branch
    WHERE 
    branch.travel_agency_branch_id = '%d' AND trip.trip_start > '%s' AND trip.trip_start < '%s' AND
    branch.travel_agency_branch_id = r.travel_agency_branch_id  AND r.offer_trip_package_id = trip.trip_package_id 
    GROUP BY  trip.trip_package_id"""%(int(x), str(a), str(b))

    cur.execute(sql1)
    res=cur.fetchall()
    names = []
    new_res = []
    i = 0
    
    for row in res:
        new = row[0]
        sql2="""SELECT e.name, e.surname
        FROM employees e, trip_package trip, guided_tour g, travel_guide trv
        WHERE trip.trip_package_id = '%d' AND  g.travel_guide_employee_AM = e.employees_AM AND g.trip_package_id = trip.trip_package_id
        GROUP BY e.employees_AM"""%(int(new))
        cur.execute(sql2)
        names = cur.fetchall()
        list_row = list(row) 
        list_row.append(names)
        new_row = tuple(list_row)
        new_res.append(new_row)

    return [("Trip_ID", "Cost_Per_Person","Max_Num_Participants", "Reservations","Remaining Slots","Trip_Start", "Trip_End", "Guides"),] + list(new_res)


def findRevenue(x):
    
   # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()

    sql2 = """SELECT branch.travel_agency_branch_id, COUNT(DISTINCT r.Reservation_id),COUNT(DISTINCT r.Reservation_id)*trip.cost_per_person, COUNT(e.employees_AM), sum(e.salary) FROM travel_agency_branch AS branch, reservation AS r,offer AS o, employees AS e, trip_package AS trip WHERE branch.travel_agency_branch_id = e.travel_agency_branch_travel_agency_branch_id AND branch.travel_agency_branch_id = r.travel_agency_branch_id AND r.offer_trip_package_id = trip.trip_package_id AND o.offer_id = r.offer_id GROUP BY branch.travel_agency_branch_id ORDER BY COUNT(DISTINCT r.Reservation_id)*trip.cost_per_person %s"""%(str(x))
    
    cur.execute(sql2)
    res=cur.fetchall()


    return [("travel_agency_branch_id", "total_num_reservations", "total_income", "total_num_employees", "total_salary"),] + list(res)



def bestClient(x):

    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    # select maximum revenue
    sql1 = """SELECT sum(o.cost), tr.name, tr.surname
    FROM offer o, traveler tr, reservation r
    WHERE tr.traveler_id = r.Customer_id and r.offer_id = o.offer_id
    GROUP BY tr.traveler_id
    ORDER BY sum(o.cost) DESC"""

    cur.execute(sql1)
    travelers = cur.fetchall()
    
    print(travelers[0])
    traveler0 = travelers[0]
    max_revenue = traveler0[0]
    best_travelers = []
    i = 0
    attractions = []
    result = []
    for trav in travelers:
        revenue = trav[0]
        if revenue == max_revenue :

            sql = """SELECT  tr.traveler_id, tr.name, tr.surname, count(distinct d.name), count( distinct d.country)
            FROM offer o, traveler tr, reservation r , destination d, trip_package_has_destination trhd
            WHERE  tr.name = 'Bernard'and tr.surname = 'Pollich' and r.Customer_id = tr.traveler_id and r.offer_id = o.offer_id
            and trhd.destination_destination_id = d.destination_id and trhd.trip_package_trip_package_id = o.trip_package_id;"""

            cur.execute(sql)
            best_travelers = cur.fetchall()

            sql = """SELECT  attr.name
            FROM offer o, traveler tr, reservation r , destination d, trip_package_has_destination trhd,tourist_attraction attr, guided_tour g
            WHERE  tr.name = 'Bernard'and tr.surname = 'Pollich' and r.Customer_id = tr.traveler_id and r.offer_id = o.offer_id
            and trhd.destination_destination_id = d.destination_id and trhd.trip_package_trip_package_id = o.trip_package_id 
            and d.destination_id = attr.destination_destination_id and g.trip_package_id = trhd.trip_package_trip_package_id and g.tourist_attraction_id = attr.tourist_attraction_id
            GROUP BY attr.tourist_attraction_id;"""

            cur.execute(sql)
            attractions = cur.fetchall()

            # with_attractions = (best_travelers[0][0], best_travelers[0][1], attractions)
            # # without_attractions = list(best_travelers[i])
            # # without_attractions.append(list(attractions))

            # # with_attractions = tuple(without_attractions)
            # best_travelers = (with_attractions)
            list_row = list(best_travelers[i]) 
            list_row.append(attractions)
            new_row = tuple(list_row)
            result.append(new_row)
            
        else : 
            break
        i+=1
        
   
    
    return [("Traveler_id","First Name", "Last Name", "Countries Visited", "Cities Visited", "Sights Visited")] + list(result)

    
    
    
    

def giveAway(N):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()


    sql1="""SELECT trip.trip_package_id FROM trip_package trip """
    cur.execute(sql1)
    trip_id= cur.fetchall()

    sql2="""SELECT trav.traveler_id FROM traveler trav"""
    cur.execute(sql2)
    traveler_id = cur.fetchall()
    random_travelers = []
    random_travelers = random.sample(traveler_id, k = int(N))


    # Initialize a list to store return messages
    return_messages = []

    for traveler in random_travelers:
        # get all the destination the lucky-one have already travel
        sql3="""SELECT trip.trip_package_id
        FROM trip_package as trip, traveler as tr, reservation as r
        WHERE tr.traveler_id = '%d' AND r.Customer_id = tr.traveler_id AND trip.trip_package_id = r.offer_trip_package_id """%(int(traveler[0]))
        
        print("\ TRAVELER ID")
        print(int(traveler[0]))

        
        cur.execute(sql3)
        old_trips = cur.fetchall()

        # find the new trip
        new_possible_trips = list(filter(lambda x: x not in list(old_trips), list(trip_id)))
        new_trip = (random.choice(list(new_possible_trips)))
        print("new trip")
        print(new_trip)

        #Remove the new randomly chosen trip_id from the possible trips of the FUTURE!

        list(trip_id).remove(new_trip)

        sql4 = """SELECT trip.cost_per_person
        FROM trip_package as trip
        WHERE trip.trip_package_id = '%d' """%(int(new_trip[0]))

        cur.execute(sql4)
        tuple = cur.fetchone()
        cost_per_person = tuple[0]

        offer_info_category = "full-price"
        # check for 25% discount
        if len(old_trips) > 1 :
            cost_per_person = float(cost_per_person*75/100)
            print("\ncost per person")
            print(cost_per_person)
            print("\nold trips")
            print(len(old_trips))
            offer_info_category = " group-discount"


        # find the new offer_id
        sql5 = """SELECT offer.offer_id
        FROM offer 
        ORDER BY offer.offer_id DESC"""

        cur.execute(sql5)
        tuple = cur.fetchall()
        offer_id = tuple[0]
        new_offer_id = int(offer_id[0]) +1
        print("\nnew offer")
        print(new_offer_id)


        # choose as starting day today
        start_date = '2023/05/03'
        end_date = '2023/08/03'

        print("\ndates")
        print(start_date,end_date)


        # take travelers name surname and gender
        sql6 = """SELECT tr.name, tr.surname, tr.gender
        FROM  traveler as tr
        WHERE tr.traveler_id = '%d'"""%(int(traveler[0]))
        cur.execute(sql6)
        tuple = cur.fetchall()
        tuple = tuple[0]

        print("tuple")
        print(tuple[0])
        print(tuple[1])
        print(tuple[2])
       
        name = tuple[0]
        surname = tuple[1]
        gender = tuple[2]

        # make the right address depending on gender
        addr = "Ms"
        if gender == "male" :
            addr = "Mr"
            

        # take destination -or- destinations name
        sql7 = """SELECT d.name
        FROM trip_package as trip, trip_package_has_destination as trhd, destination as d
        WHERE trip.trip_package_id = '%d' AND trhd.destination_destination_id = d.destination_id AND trip.trip_package_id = trhd.trip_package_trip_package_id """%(int(new_trip[0]))
        cur.execute(sql7)
        dest = cur.fetchall()
        dest = [d[0] for d in dest] 
        description = "travel the world with as"

        # start_date = "2023/05/03"
        # end_date = "2023/08/03"
   

        sqlInsert="""INSERT INTO offer(offer_id, offer_start, offer_end, cost, description, trip_package_id,offer_info_category)
                     VALUES (%s,%s,%s, %s,%s,%s, %s)"""

        try:
            # Execute the SQL command
            cur.execute(sqlInsert,(int(new_offer_id),start_date,end_date,float(cost_per_person),description,int(new_trip[0]),offer_info_category))
            # Commit your changes in the database
            con.commit()
        except Exception as e:
            # Rollback in case there is any error
            con.rollback()
            print("Error:", e)

    
        return_mess = """Congratulations _{}  {} {}!
                    Pack your bags and get ready to enjoy {}! At ART TOUR travel we
            acknowledge you as a valued customer and we’ve selected the most incredible
            tailor-made travel package for you. We offer you the chance to travel to {}
            at the incredible price of {}. Our offer ends on {}. Use code
            OFFER {} to book your trip. Enjoy these holidays that you deserve so much\n""".format(addr,name,surname,description," and ".join(dest),int(cost_per_person),end_date,new_offer_id)

        return_messages.append(return_mess)



    return [("winner", message) for message in return_messages]