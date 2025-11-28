import React from 'react';
import { Route, Switch, Redirect } from 'react-router-dom';
import MainPage from './pages/MainPage';
import ReportDesignerPage from './pages/ReportDesignerPage';

function App() {
  return (
    <Switch>
      <Route exact path="/" component={MainPage} />
      <Route exact path="/reports" component={ReportDesignerPage} />
      <Route exact path="/reports/:id" component={ReportDesignerPage} />
      <Redirect to="/" />
    </Switch>
  );
}

export default App;

