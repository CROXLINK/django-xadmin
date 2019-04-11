import React from 'react'
import { OverlayTrigger, Tooltip, Card, Form, Row, Col, Button, Modal } from 'react-bootstrap'
import app from 'xadmin'
import Icon from 'react-fontawesome'

const FormLayout = props => {
  const { children, invalid, handleSubmit, onDelete, schema, submitting } = props
  const { _t } = app.context
  const icon = submitting ? 'spinner fa-spin' : 'floppy-o'

  return (
    <Form onSubmit={handleSubmit}>
      <Card className="mt-3 mb-3" body>
        {children}
        <Form.Group as={Row} className="mt-5">
          <Col sm={{ span: 10, offset: 2 }}>
            {invalid ? (
              <OverlayTrigger placement="top" overlay={<Tooltip>{_t('Please be sure to complete all field')}</Tooltip>}>
                <Button key={0} type="submit" disabled={submitting} onClick={handleSubmit} variant="primary">
                  <Icon name="ban"/> {_t('Save')}</Button>
              </OverlayTrigger>
            ) : (
              <Button key={0} type="submit" disabled={submitting} onClick={handleSubmit} variant="primary">
                <Icon name={icon}/> {_t('Save')}</Button>
            )} {' '}
            <Button key={1} onClick={()=>history.back()} variant="light">{_t('Cancel')}</Button>
          </Col>
        </Form.Group>
      </Card>
    </Form>
  )
}

const ModalLayout = ({ children, invalid, handleSubmit, submitting, title, show, onClose, saveText }) => {
  const { _t } = app.context

  return (
    <Modal show={show} size="lg" onHide={onClose}>
      <Modal.Header closeButton>{title}</Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>{children}</Form>
      </Modal.Body>
      <Modal.Footer>
        <Button key={0} variant="light" onClick={onClose}>{_t('Close')}</Button>
        <Button key={1} type="submit" disabled={invalid || submitting}  variant="primary" onClick={handleSubmit}>
          <Icon name={submitting ? 'spinner fa-spin' : 'floppy-o'}/> {saveText || _t('Save')}
        </Button>
      </Modal.Footer>
    </Modal>
  )
}

export { FormLayout, ModalLayout }