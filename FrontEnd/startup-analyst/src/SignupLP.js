import React from "react";
import { Navbar, Nav, Container, Button, Row, Col, Card } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const SignupLP = () => {
  const navigate = useNavigate();

  return (
    <div>
      {/* Navbar */}
      <Navbar expand="lg" bg="dark" variant="dark" className="px-4">
        <Navbar.Brand href="#">
          <span className="fw-bold fs-3">LV<span className="text-primary">X</span></span>
          <small className="text-light ms-2">LetsVenture</small>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav" className="justify-content-end">
          <Nav className="me-3">
            <Nav.Link href="#">For Founders</Nav.Link>
            <Nav.Link href="#">For Investors</Nav.Link>
            <Nav.Link href="#">Portfolio</Nav.Link>
            <Nav.Link href="#">Resources</Nav.Link>
          </Nav>
          <Button variant="light">LOGIN</Button>
        </Navbar.Collapse>
      </Navbar>

      {/* Hero Section */}
      <Container className="my-5">
        <Row className="justify-content-center">
          <Col md={10}>
            <Card className="p-5 shadow-lg text-white" style={{ background: "linear-gradient(90deg, #0d1b4c, #133c7e)" }}>
              <Row>
                {/* Left Card */}
                <Col md={6} className="mb-4 mb-md-0">
                  <div className="mb-3 fs-2">👥</div>
                  <p className="text-uppercase text-secondary small">
                    Investors: Back startups, build
                  </p>
                  <h3 className="fw-bold">Invest with LVX</h3>
                  <p>
                    Access vetted startups, trusted syndicates, and exclusive deals to grow your private market portfolio.
                  </p>
                  <Button 
                    variant="light" 
                    className="fw-bold"
                    onClick={() => navigate("/signup", { state: { role: "investor" } })}
                  >
                    Start Investing
                  </Button>
                </Col>

                {/* Right Card */}
                <Col md={6}>
                  <div className="mb-3 fs-2">🚀</div>
                  <p className="text-uppercase text-secondary small">
                    Founders: Raise capital, grow faster
                  </p>
                  <h3 className="fw-bold">Raise with LVX</h3>
                  <p>
                    Connect with trusted angels, family offices, and VCs to raise smart capital and strengthen your cap table.
                  </p>
                  <Button 
                    variant="light" 
                    className="fw-bold"
                    onClick={() => navigate("/signup", { state: { role: "founder" } })}
                  >
                    Signup as a Startup
                  </Button>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default SignupLP;
