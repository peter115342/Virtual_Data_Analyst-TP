import buttonWhite from '../assets/arrow_white.svg'

export default function ButtonSend({ onClick }) {
  return (
    <button type="button" onClick={onClick} className="bg-gray-600 h-9 w-9 rounded-full hover:bg-gray-700">
      <img
        src={buttonWhite}
        alt="Send"
        className="w-full h-full object-contain p-2"
      />
    </button>
  )
}
