import { useEffect, useState } from "react";
import ButtonDatabase from "./ButtonDatabase.jsx";
import crossOrange from '../assets/cross-orange.svg';
import filterOrange from "../assets/filter-orange.svg";
import HistoryBox from "./HistoryBox.jsx";
import logo from "../assets/VDA_logo.png";
import { listSessions } from "../services/databaseService";

export default function SideBar({ isOpenS, toggle, onOpenDatabase, isConnected, onLogout, userName }) {

  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const data = await listSessions();
        setSessions(data.sessions || []);
      } catch (err) {
        console.error("Failed to load sessions:", err);
        setError("Failed to load sessions");
      }
    };

    fetchSessions();
  }, []);

  const chats = sessions.map((s) => ({
    id: s._id,
    title: s.db_name || "Unknown DB",
    description: s.connected_at
      ? new Date(s.connected_at).toLocaleString()
      : "No date"
  }));

  // const chats = [
  //   { id: 1, title: "Users table error", description: "Prečo mi nefunguje SELECT * FROM Users kde mám NULL hodnoty?" },
  //   { id: 2, title: "Join tables issue", description: "Ako správne použiť INNER JOIN medzi Orders a Customers?" },
  //   { id: 3, title: "Slow query fix", description: "Query trvá 5 sekúnd, ako optimalizovať indexy v SQLite?" },
  //   { id: 4, title: "Authentication bug", description: "Prečo sa user neprihlási aj keď JWT token existuje?" },
  //   { id: 5, title: "Database connection", description: "Ako správne napojiť React na ASP.NET Core backend?" },
  //   { id: 6, title: "Foreign key problem", description: "Prečo mi foreign key constraint padá pri delete?" },
  //   { id: 7, title: "Insert not working", description: "INSERT query sa vykoná bez erroru ale nič sa neuloží." },
  //   { id: 8, title: "Migration issue", description: "EF Core migrácie sa nevytvárajú správne." },
  //   { id: 9, title: "Filter schools", description: "Ako filtrovať školy podľa jazyka a lokácie v SQL?" },
  //   { id: 10, title: "API endpoint error", description: "Prečo mi controller vracia 500 error pri GET requeste?" },
  //   { id: 11, title: "Duplicate records", description: "Ako zabrániť duplicitným záznamom v databáze?" },
  //   { id: 12, title: "Pagination logic", description: "Ako spraviť stránkovanie výsledkov v databáze?" },
  //   { id: 13, title: "Search performance", description: "Full-text search je pomalý, čo použiť namiesto LIKE?" },
  //   { id: 14, title: "User roles system", description: "Ako implementovať role-based authorization?" },
  //   { id: 15, title: "Test results saving", description: "Ako ukladať výsledky testov pre každého používateľa?" },
  //   { id: 16, title: "Update query issue", description: "UPDATE query prepíše všetky riadky, ako to opraviť?" },
  //   { id: 17, title: "Delete cascade problem", description: "Prečo cascade delete nefunguje správne?" },
  //   { id: 18, title: "React fetch error", description: "Fetch request vracia undefined dáta z API." },
  //   { id: 19, title: "Token expiration", description: "Ako riešiť expirovaný JWT token?" },
  //   { id: 20, title: "Database schema design", description: "Ako navrhnúť databázu pre testovací portál?" },
  //   { id: 21, title: "Sorting results", description: "Ako zoradiť výsledky podľa viacerých stĺpcov?" },
  //   { id: 22, title: "Search by name", description: "Ako implementovať vyhľadávanie podľa mena?" },
  //   { id: 23, title: "Index optimization", description: "Ktoré stĺpce by mali mať index?" },
  //   { id: 24, title: "Null values handling", description: "Ako správne pracovať s NULL hodnotami v SQL?" },
  //   { id: 25, title: "Backend validation", description: "Ako validovať vstupy na serveri?" },
  //   { id: 26, title: "Frontend form bug", description: "Formulár neposiela dáta správne do backendu." },
  //   { id: 27, title: "API routing issue", description: "Routing v ASP.NET Core nefunguje správne." },
  //   { id: 28, title: "Database seeding", description: "Ako naplniť databázu testovacími dátami?" },
  //   { id: 29, title: "User registration error", description: "Registrácia hádže error pri ukladaní usera." },
  //   { id: 30, title: "Performance improvement", description: "Ako zrýchliť načítanie dát v aplikácii?" }
  // ];

  return (
    <div className="h-full min-h-0 p-1 flex flex-col bg-[#E8E8E8]">

      <div className="flex items-center justify-between">
        {isOpenS && (
          <img src={logo} alt="Logo" className="w-18" />
        )}

        <button
          onClick={toggle}
          className="w-10 h-10 flex items-center justify-center rounded-full hover:brightness-85"
        >
          <img
            src={isOpenS ? crossOrange : filterOrange}
            alt=""
            className={isOpenS ? "w-6" : "w-7"}
          />
        </button>
      </div>

      {isOpenS && (
        <div className="flex flex-col items-center gap-4 flex-1 min-h-0 bg-[#E8E8E8]">
          {error && (
            <div className="text-red-500 text-xs w-full px-2">
              {error}
            </div>
          )}

          <div className="flex-1 w-full overflow-y-auto mt-2 space-y-1 pr-1 custom-scrollbar min-h-0">            {chats.length === 0 && !error && (
              <div className="text-gray-500 text-sm px-2">
                No sessions yet
              </div>
            )}

            {chats.map(chat => (
              <HistoryBox 
                key={chat.id}
                title={chat.title}
                description={chat.description}
              />
            ))}
          </div>

        </div>
      )}
    </div>
  );
}