import { fireEvent, render } from '@testing-library/react';
import Upload_ReactComponent from '../components/Upload_ReactComponent.react.js';


describe('Initial Render', () => {
  const mockSetProps = jest.fn(a => console.log(a));

  test('renders a div', () => {
    const { container } = render(<Upload_ReactComponent setProps={mockSetProps}></Upload_ReactComponent>);
    expect(container.tagName.toLowerCase()).toEqual('div');
  });

  test('prompts the user to select a file', () => {
    const { getByText } = render(<Upload_ReactComponent setProps={mockSetProps}></Upload_ReactComponent>);
    expect(getByText('Click Here to Select a File')).toBeTruthy();
    expect(getByText('Click Here to Select a File').tagName.toLowerCase()).toEqual('label');
  });

  test('includes a file upload input field', () => {
    const { getByLabelText } = render(<Upload_ReactComponent setProps={mockSetProps}></Upload_ReactComponent>);
    getByLabelText('Click Here to Select a File');
    expect(getByLabelText('Click Here to Select a File').tagName.toLowerCase()).toEqual('input');
    expect(getByLabelText('Click Here to Select a File').type).toEqual('file');
  });
});

describe('Class Parsing', () => {
  const mockSetProps = jest.fn(a => console.log(a));

  test('has only the default class when no props are passed', () => {
    const { container } = render(<Upload_ReactComponent setProps={mockSetProps}></Upload_ReactComponent>);
    expect(container.firstChild.classList.contains('dash-uploader-default')).toBeTruthy();
  });

  test('has the default class and the disabled class when disabled = true', () => {
    const { container } = render(<Upload_ReactComponent setProps={mockSetProps} disabled={true}></Upload_ReactComponent>);
    expect(container.firstChild.classList.contains('dash-uploader-default')).toBeTruthy();
    expect(container.firstChild.classList.contains('dash-uploader-disabled')).toBeTruthy();
  });

  test('has the default class and hovered class when object is hovered', () => {
    const { container, getByText } = render(<Upload_ReactComponent setProps={mockSetProps}></Upload_ReactComponent>);
    fireEvent.mouseEnter(getByText('Click Here to Select a File'));
    expect(container.firstChild.classList.length).toEqual(2);
    expect(container.firstChild.classList.contains('dash-uploader-default')).toBeTruthy();
    expect(container.firstChild.classList.contains('dash-uploader-hovered')).toBeTruthy();
  });

  test('does not have the hovered class when disabled = true and object is hovered', () => {
    const { container } = render(<Upload_ReactComponent setProps={mockSetProps} disabled={true}></Upload_ReactComponent>);
    fireEvent.mouseOver(container.firstChild);
    expect(container.firstChild.classList.length).toEqual(2);
    expect(container.firstChild.classList.contains('dash-uploader-default')).toBeTruthy();
    expect(container.firstChild.classList.contains('dash-uploader-disabled')).toBeTruthy();
    expect(container.firstChild.classList.contains('dash-uploader-hovered')).toBeFalsy();
  });
});
