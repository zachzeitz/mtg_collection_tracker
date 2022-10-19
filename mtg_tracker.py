import json
import requests
from tkinter import *
from tkinter import ttk
import sqlite3

root= Tk()
root.title("MTG Collection Tracker")
root.geometry("700x600")

#create of connect to database
conn= sqlite3.connect('mtg_card_collection.db')
c=conn.cursor()

'''
c.execute("""CREATE TABLE owned_cards (
    card_name text,
    card_set text,
    card_prices text,
    card_quantity int,
    add_criteria text
)""")
'''
sets_list= []
prices_dict={}

query_label=Label(root)
clicked= StringVar()
def submit():
    global api_printings
    global num_owned_input
    
    #create button to find price for selected card and set
    search_price_button= Button(root, text="Search Price", command=search_price)
    search_price_button.grid(row=5, column=0, padx=10, pady=10, columnspan=2, ipadx=110, sticky=N)

    #Create Button to Add Card to Database
    record_button= Button(root, text="Add Card To Database", command=add_to_database)
    record_button.grid(row=6, column=0, padx=10, pady=10,columnspan=2, ipadx= 85, sticky=N)

    sets_list.clear()

    try:
        api_request_card= requests.get(f'https://api.scryfall.com/cards/named?exact={display_name_input.get()}')
        api_card= json.loads(api_request_card.content)
    except Exception as e:
        api_card= "Error..."

    try:
        api_request_printings= requests.get(api_card['prints_search_uri'])
        api_printings= json.loads(api_request_printings.content)
    except Exception as e:
        api_printings="Error on Printings..."

    for printing in api_printings['data']:
        sets_list.append(printing["set_name"])
    
    clicked.set(sets_list[0])
    display_set_label=Label(root, text="Set Name")
    display_set_label.grid(row=1, column=0, padx=10, pady=10)
    display_set= OptionMenu(root, clicked, *sets_list)
    display_set.grid(row=1, column=1, padx=10, pady=10)

    #display_name_input.delete(0, END)

def search_price():
    global choice
    global current_prices
    global num_owned_input

    num_owned_input=Entry(root)
    num_owned_input.grid(row=3, column=1, padx=10, pady=10)
    
    choice= clicked.get()

    for printing in api_printings['data']:
        prices_dict.update({(printing['set_name']):(printing['prices'])})

    for k,v in prices_dict.items():
        if k == choice:
            current_prices= Label(root, text=prices_dict[k])
    current_prices.grid(row=2, column=1, padx=10, pady=10)

    #create Label for prices
    prices_label= Label(root, text="Current Prices")
    prices_label.grid(row=2, column=0, padx=10, pady=10)

    num_owned=Label(root, text="Number of Copies Owned")
    num_owned.grid(row=3, column=0, padx=10, pady=10, sticky=W)


def add_to_database():
    #create of connect to database
    conn= sqlite3.connect('mtg_card_collection.db')
    c=conn.cursor()
    card_quantity= num_owned_input.get()

    # insert into table
    c.execute("INSERT into owned_cards VALUES (:card_name, :card_set, :card_prices, :card_quantity, :add_criteria)",
    {
        'card_name': display_name_input.get(),
        'card_set': choice,
        'card_prices': current_prices.cget("text"),
        'card_quantity': card_quantity,
        'add_criteria': extra_criteria_input.get()
    })

    conn.commit()
    conn.close()

    num_owned_input.delete(0, END)

def get_cards():
    global info
    r=1

    top= Toplevel()
    top.geometry("1100x850")
    top.title("Archived Collection")

    #create maine frame
    main_frame= Frame(top)
    main_frame.pack(fill=BOTH, expand=1)

    #create canvas
    my_canvas= Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    #Add scroolbar to canvas
    my_scrollbar= ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)

    #Configure canvas
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

    #create another frame inside the canvas
    second_frame= Frame(my_canvas)

    #add that new frame to a window in the canvas
    my_canvas.create_window((0,0), window=second_frame, anchor="nw")

    card_names=Label(second_frame, text="Card Name",font=('Times New Roman', 16, 'bold'))
    card_names.grid(row=0, column=0)
    card_sets=Label(second_frame, text="Set",font=('Times New Roman', 14, 'bold'))
    card_sets.grid(row=0, column=1)
    card_price=Label(second_frame, text="Prices (as of day catalogued)", font=('Times New Roman', 14, 'bold'))
    card_price.grid(row=0, column=2)
    cards_quantity=Label(second_frame, text="Number Owned", font=('Times New Roman', 14, 'bold'))
    cards_quantity.grid(row=0, column=3)
    add_criteria=Label(second_frame, text="Alternate Versions", font=('Times New Roman', 14, 'bold'))
    add_criteria.grid(row=0, column=4, padx=10)

    #create of connect to database
    conn= sqlite3.connect('mtg_card_collection.db')
    c=conn.cursor()

    c.execute('select * from owned_cards')
    info= c.fetchall()
    for x in info:
        if x[3] == 0:
            continue 
        collected_card_names= Label(second_frame, text=x[0])
        collected_card_names.grid(row=r, column=0, padx=10, pady=10)
        collected_cards_sets=Label(second_frame, text=x[1])
        collected_cards_sets.grid(row=r, column=1, padx=10, pady=10)
        collected_cards_prices=Label(second_frame, text=x[2])
        collected_cards_prices.grid(row=r, column=2, padx=10, pady=10)
        collected_cards_quantity=Label(second_frame, text=x[3])
        collected_cards_quantity.grid(row=r, column=3, padx=10, pady=10)
        add_criteria_saved=Label(second_frame, text=x[4])
        add_criteria_saved.grid(row=r, column=4, padx=10, pady=10)
        r +=1

    conn.close()

def query_collection():
    conn= sqlite3.connect('mtg_card_collection.db')
    c=conn.cursor()
    c.execute('select * from owned_cards')

    collected= c.fetchall()
    #print(type(collected))

    queried_card= query_collection_input.get()
    for x in collected:
        if queried_card == x[0]:
            print(x)

    conn.close()


display_name_label=Label(root, text="Enter Card Name (Be Exact)")
display_name_label.grid(row=0, column=0, padx=10, pady=10, sticky=W)

#Create Text Boxes
display_name_input= Entry(root)
display_name_input.grid(row=0, column=1, padx=250, pady=10, sticky=W) 

#create submit button to ping API
submit_button = Button(root, text="Search For Card", command=submit)
submit_button.grid(row=5, column=0, padx=10, pady=10, columnspan=2, ipadx=100,sticky=N)

#create button to show collection in 2nd window
collected_button = Button(root, text="Show Collection", command=get_cards)
collected_button.grid(row=8, column=0, padx=10, pady=10, columnspan=2, ipadx=100,sticky=N)

#create button, label, and entry to search collection for specific card
query_collection_label=Label(root, text="Enter Card Name (Be Exact)")
query_collection_label.grid(row=9, column=0, padx=10, pady=10, sticky=W)

#create input for card name to be queried in database
query_collection_input= Entry(root)
query_collection_input.grid(row=9, column=1, padx=250, pady=10, sticky=W)

#Create button to search for card in collected database
collected_button = Button(root, text="Search Collection For Card", command=query_collection)
collected_button.grid(row=10, column=0, padx=10, pady=10, columnspan=2, ipadx=70,sticky=N)

#Create input box for additional criteria (foil, borderless, expanded art, alternate art, etc.)
extra_criteria_label=Label(root, text="Enter Additional Criteria (Borderless, Foil, etc.)")
extra_criteria_label.grid(row=4, column=0, padx=10, pady=10, sticky=W)

extra_criteria_input= Entry(root)
extra_criteria_input.grid(row=4, column=1, padx=250, pady=10, sticky=W) 

conn.close()

root.mainloop()