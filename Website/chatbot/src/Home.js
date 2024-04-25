import Header from "./Header";
import Footer from "./Footer";
import Main from "./Main";
import Nav from "./Nav";
import Chatbot from "./Chatbot";

const Home = () => {
    return (
        <div>
            <Header></Header>
            <Nav></Nav>
            <Main></Main>
            <Chatbot></Chatbot>
            <Footer></Footer>
        </div>
      );
};

export default Home;