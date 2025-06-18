import type React from 'react'
import { useCallback, useState } from 'react'

type FormElement = HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement

type OptionsProp = React.DetailedHTMLProps<React.InputHTMLAttributes<HTMLInputElement>, HTMLInputElement> & {
  onChange?: (e: React.ChangeEvent<FormElement> | unknown) => void
  onBlur?: (e: React.FocusEvent<FormElement> | unknown) => void
  transform?: (val: string) => string
}

type FileOptionsProp = Omit<OptionsProp, 'onChange'> & {
  onChange?: (files: File[]) => void
}

type KeysWithStrings<P> = {
  [K in keyof P]: P[K] extends string | null | undefined ? K : never
}[keyof P]

type KeysWithStringsArray<P> = {
  [K in keyof P]: P[K] extends string[] | null | undefined ? K : never
}[keyof P]

type KeysWithNumbers<P> = {
  [K in keyof P]: P[K] extends number | null | undefined ? K : never
}[keyof P]

type KeysWithBooleans<P> = {
  [K in keyof P]: P[K] extends boolean | null | undefined ? K : never
}[keyof P]

type KeysWithDates<P> = {
  [K in keyof P]: P[K] extends Date | null | undefined ? K : never
}[keyof P]

type KeysWithObjects<P> = {
  [K in keyof P]: P[K] extends object | null | undefined ? K : never
}[keyof P]

export const useFormState = <T>(_initialState: T) => {
  const [initialState, _setInitialState] = useState<T>(_initialState)
  const [values, setValues] = useState<T>(_initialState)
  const [dirty, setDirtyItems] = useState<Set<keyof T>>(new Set<keyof T>())
  const [touched, setTouchedItems] = useState<Set<keyof T>>(new Set<keyof T>())
  const [validationReadyFields, setValidationReadyFields] = useState<Set<keyof T>>(new Set<keyof T>())

  const isDirty = dirty.size > 0
  const isTouched = touched.size > 0

  const fieldDirty = useCallback((value: unknown, state: T, name: keyof T) => {
    if (typeof value === 'object') {
      return JSON.stringify(value) !== JSON.stringify(state[name])
    }

    return value !== state[name]
  }, [])

  const resetState = () => {
    setValidationReadyFields(new Set())
    setTouchedItems(new Set())
    setDirtyItems(new Set())
  }

  const resetValues = () => {
    setValues(initialState)
  }

  const reset = () => {
    resetState()
    resetValues()
  }

  // biome-ignore lint/correctness/useExhaustiveDependencies: only when initialState changes
  const setValue = useCallback(
    (name: keyof T, value: unknown, makeTouched = true, makeDirty = true) => {
      setValues((state) => ({
        ...state,
        [name]: value,
      }))

      makeTouched && setTouchedItems((state) => state.add(name))

      if (makeDirty) {
        if (initialState?.[name]) {
          if (fieldDirty(value, initialState, name)) {
            setDirtyItems((state) => state.add(name))
          } else {
            setDirtyItems((state) => {
              state.delete(name)
              return state
            })
          }
        } else {
          if (value === '' || value === false) {
            setDirtyItems((state) => {
              state.delete(name)
              return state
            })
          } else {
            setDirtyItems((state) => state.add(name))
          }
        }
      }
    },
    [initialState],
  )

  const setInitialState = useCallback((state: T) => {
    _setInitialState(state)
    setValues(state)
    setDirtyItems(new Set())
    setTouchedItems(new Set())
  }, [])

  const clear = useCallback((name: string) => {
    setValues((state) => ({
      ...state,
      [name]: '',
    }))

    setDirtyItems(new Set())
    setTouchedItems(new Set())
  }, [])

  const updateReadyToValidateFields = (val: string | unknown, name: keyof T) => {
    setValidationReadyFields((state) => new Set([...state, name]))
  }

  const text = (name: keyof T, options: OptionsProp = {}) => {
    const { onChange, onBlur, transform = (val: string) => val } = options

    return {
      type: 'text' as const,
      name,
      get value() {
        return (values?.[name] as string) ?? ''
      },
      onBlur: (e: React.FocusEvent<FormElement>) => {
        updateReadyToValidateFields(e.target.value, name)
        onBlur?.(e)
      },
      onChange: (e: React.ChangeEvent<FormElement>) => {
        setValue(name, transform(e.target.value))
        onChange?.(e)
      },
    }
  }

  const password = (name: KeysWithStrings<T>, options: OptionsProp = {}) => {
    const { onChange, onBlur, transform = (val: string) => val } = options

    return {
      type: 'password' as const,
      name,
      get value() {
        return values?.[name] ?? ''
      },
      onBlur: (e: React.FocusEvent<HTMLInputElement>) => {
        updateReadyToValidateFields(e.target.value, name)
        onBlur?.(e)
      },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(name, transform(e.target.value))
        onChange?.(e)
      },
    }
  }

  const hidden = (name: keyof T, options: OptionsProp = {}) => {
    const { onChange, transform = (val: string) => val } = options

    return {
      type: 'hidden' as const,
      name,
      get value() {
        return values?.[name] ?? ''
      },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(name, transform(e.target.value))
        onChange?.(e)
      },
    }
  }

  const number = (name: KeysWithNumbers<T>, options: OptionsProp = {}) => {
    const { onChange, onBlur } = options

    return {
      type: 'number' as const,
      name,
      get value() {
        const val = values?.[name]
        const isEmpty = val === undefined || val === null
        return isEmpty ? undefined : Number(val)
      },
      onBlur: (e: React.FocusEvent<HTMLInputElement>) => {
        updateReadyToValidateFields(e.target.value, name)
        onBlur?.(e)
      },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value === '' ? undefined : Number(e.target.value)

        if (val === undefined || Number.isNaN(val)) {
          setValue(name, undefined)
        } else {
          setValue(name, val)
        }

        onChange?.(e)
      },
    }
  }

  const date = (name: KeysWithStrings<T>, options: OptionsProp = {}) => {
    const { onChange, onBlur, transform = (val: string) => val } = options

    return {
      type: 'date' as const,
      name,
      get value() {
        return values?.[name] ?? ''
      },
      onBlur: (e: React.FocusEvent<HTMLInputElement>) => {
        updateReadyToValidateFields(e, name)
        onBlur?.(e)
      },
      onChange: (event: React.ChangeEvent<HTMLInputElement>) => {
        setValue(name, transform(event.target.value))
        onChange?.(event)
      },
    }
  }

  const email = (name: KeysWithStrings<T>, options: OptionsProp = {}) => {
    const { onChange, onBlur, transform = (val: string) => val } = options

    return {
      type: 'email' as const,
      name,
      get value() {
        return values?.[name] ?? ''
      },
      onBlur: (e: React.FocusEvent<HTMLInputElement>) => {
        updateReadyToValidateFields(e.target.value, name)
        onBlur?.(e)
      },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(name, transform(e.target.value))
        onChange?.(e)
      },
    }
  }

  const radio = (name: keyof T, value: T, options: OptionsProp = {}) => {
    const { onChange } = options
    return {
      type: 'radio' as const,
      name,
      value,
      get checked() {
        return values?.[name] === value
      },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(name, e.target.value)
        onChange?.(e)
      },
    }
  }

  const checkbox = (name: KeysWithBooleans<T> | KeysWithNumbers<T>, options: OptionsProp = {}) => {
    const { onChange } = options

    return {
      type: 'checkbox' as const,
      name,
      get checked() {
        return !!values?.[name]
      },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(name, e.target.checked)

        onChange?.(e)
      },
    }
  }

  const checkboxArray = (name: keyof T, value: string, options: OptionsProp = {}) => {
    const { onChange } = options

    return {
      name,
      value,
      get checked() {
        return ((values?.[name] as Array<string>) ?? []).includes(value)
      },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        const copy = Object.assign([] as string[], values?.[name])

        if (e.target.checked) {
          copy.push(value)
        } else {
          const index = copy.indexOf(value)

          if (index > -1) {
            copy.splice(index, 1)
          }
        }

        setValue(name, copy)

        onChange?.(e)
      },
    }
  }

  const selectMultiple = (name: KeysWithStringsArray<T>, options: OptionsProp = {}) => {
    const { onChange, onBlur } = options
    return {
      name,
      get value() {
        return values?.[name] ?? []
      },
      onBlur: (value: unknown) => {
        updateReadyToValidateFields(value, name)
        onBlur?.(null)
      },
      onChange: (value: unknown) => {
        setValue(name, value)
        onChange?.(value)
      },
    }
  }

  // This one is always going to return the raw event values
  // of a component so you can use it with whatever you want.
  const raw = <Type extends string | number | boolean | Date | string[] | object | undefined>(
    name: Type extends string
      ? KeysWithStrings<T>
      : Type extends string[]
        ? KeysWithStringsArray<T>
        : Type extends number
          ? KeysWithNumbers<T>
          : Type extends boolean
            ? KeysWithBooleans<T>
            : Type extends Date
              ? KeysWithDates<T>
              : KeysWithObjects<T>,
    options: OptionsProp = {},
  ) => {
    const { onChange, onBlur } = options
    return {
      name,
      get value() {
        return (values?.[name] ?? undefined) as Type extends string[]
          ? string[] | null | undefined
          : Type extends number
            ? number | null | undefined
            : Type extends boolean
              ? boolean | null | undefined
              : Type extends Date
                ? Date | null | undefined
                : Type extends object
                  ? Type | null | undefined
                  : string | null | undefined
      },
      onBlur: (value: unknown) => {
        updateReadyToValidateFields(value, name)
        onBlur?.(null)
      },
      onChange: (value: unknown) => {
        setValue(name, value)
        onChange?.(value)
      },
    }
  }

  const files = (name: keyof T, options: FileOptionsProp = {}) => {
    const { onChange, onBlur } = options
    return {
      name,
      get value() {
        return values?.[name] ?? undefined
      },
      onBlur: (value: unknown) => {
        updateReadyToValidateFields(value, name)
        onBlur?.(null)
      },
      onChange: (value: File[]) => {
        setValue(name, value)
        onChange?.(value)
      },
    }
  }

  return [
    values,
    {
      // Input types methods
      text,
      password,
      hidden,
      number,
      files,
      date,
      email,
      radio,
      checkbox,
      checkboxArray,
      selectMultiple,
      raw,

      // Direct access methods
      setValue,
      clear,
      setInitialState,
      dirty,
      touched,
      validationReadyFields,

      reset,
      resetState,
      resetValues,

      // Form states
      isDirty,
      isTouched,
    },
  ] as const
}
