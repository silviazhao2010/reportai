import React from 'react';
import { Route, Switch, Redirect } from 'react-router-dom';
import MainPage from './pages/MainPage';

function App() {
  return (
    <Switch>
      <Route exact path="/" component={MainPage} />
      <Redirect to="/" />
    </Switch>
  );
}

export default App;

